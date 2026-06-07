import unittest
from unittest.mock import patch, MagicMock

from kgtool.interface import ChemKG
from requests.exceptions import InvalidSchema

from services.img_extraction.extraction_queries import Queries
from services.img_extraction.extraction_worker import ExtractionWorker

query__get_some_publication_wo_img = "get_publication"
publication_doi = "DOI"
query__get_download_link_with_given_doi = "get_download_link"
download_link = "http://link.com"


class MockChemKG(ChemKG):
    def runSparql(self, query):
        if query == '':  # so an invalid query
            return {
                'data': {
                    'runSparql': 'ERROR'
                }
            }
        elif query == query__get_some_publication_wo_img:
            return {
                'data': {
                    'runSparql': f'{{"results": {{"bindings": [{{"doi": {{"value": "{publication_doi}"}}}}]}}}}'
                }
            }
        elif query == query__get_download_link_with_given_doi:
            return {
                'data': {
                    'runSparql': f'{{"results": {{"bindings": [{{"doi": {{"value": "{publication_doi}"}}}}, {{"downloadURL": {{"value": "{download_link}"}}}}]}}}}'
                }
            }


class MockChemKG_InvalidUrl(ChemKG):
    def runSparql(self, query):
        raise InvalidSchema()


class MockQueries(Queries):
    @staticmethod
    def get_some_publication_wo_img():
        return query__get_some_publication_wo_img

    @staticmethod
    def get_download_link_with_given_doi(doi: str):
        return query__get_download_link_with_given_doi


class MockQueries_Invalid(Queries):
    @staticmethod
    def get_some_publication_wo_img():
        return ""

    @staticmethod
    def get_download_link_with_given_doi(doi: str):
        return ""


class TestExtractionWorker(unittest.TestCase):

    def create_worker(self, chemkg_mock, queries_mock):
        path = 'services.img_extraction.extraction_worker'
        with patch(f'{path}.ChemKG', chemkg_mock), patch(f'{path}.Queries', queries_mock):
            worker = ExtractionWorker()
        return worker

    def test__ask_for_task__invalid_chemkg(self):
        worker = self.create_worker(MockChemKG_InvalidUrl, MockQueries)
        with self.assertRaises(Exception):
            worker._ask_for_task()

    def test__ask_for_task__invalid_query(self):
        worker = self.create_worker(MockChemKG, MockQueries_Invalid)
        with self.assertRaises(Exception):
            worker._ask_for_task()

    def test__ask_for_task__no_task(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._chemkg.runSparql = MagicMock(side_effect=lambda query: {
            'data': {
                'runSparql': '{"results": {"bindings": []}}'
            }
        })

        result = worker._ask_for_task()
        self.assertFalse(result)
        self.assertIsNone(worker._publication_doi)

    def test__ask_for_task__unexpected_return_pattern(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._chemkg.runSparql = MagicMock(side_effect=lambda query: {
            'data': {
                'runSparql': '{"results": {"bindings": ["note": {"type": "literal", "value": "intended-application:text-mining"}]}}'
            }
        })
        with self.assertRaises(Exception):
            worker._ask_for_task()

    def test__ask_for_task__valid(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        result = worker._ask_for_task()
        self.assertTrue(result)
        self.assertEqual(worker._publication_doi, publication_doi)

    def test__execute_task__invalid_chemkg(self):
        worker = self.create_worker(MockChemKG_InvalidUrl, MockQueries)
        worker._publication_doi = publication_doi
        with self.assertRaises(Exception):
            worker._execute_task()

    def test__execute_task__invalid_query(self):
        worker = self.create_worker(MockChemKG, MockQueries_Invalid)
        worker._publication_doi = publication_doi
        with self.assertRaises(Exception):
            worker._execute_task()

    def test__execute_task__no_task(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = None
        with self.assertRaises(Exception):
            worker._execute_task()

    def test__execute_task__unexpected_return_pattern(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi

        # case: doi missing
        worker._chemkg.runSparql = MagicMock(side_effect=lambda query: {
            'data': {
                'runSparql': f'{{"results": {{"bindings": [{{"downloadURL": {{"value": "{download_link}"}}}}]}}}}'
            }
        })
        with self.assertRaises(Exception):
            worker._execute_task()

        # case: download url missing
        worker._chemkg.runSparql = MagicMock(side_effect=lambda query: {
            'data': {
                'runSparql': f'{{"results": {{"bindings": [{{"doi": {{"value": "{publication_doi}"}}]}}}}'
            }
        })
        with self.assertRaises(Exception):
            worker._execute_task()

    def test__execute_task__unexpected_doi(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        worker._chemkg.runSparql = MagicMock(side_effect=lambda query: {
            'data': {
                'runSparql': f'{{"results": {{"bindings": [{{"doi": {{"value": "other_doi"}}}}, {{"downloadURL": {{"value": "{download_link}"}}}}]}}}}'
            }
        })
        with self.assertRaises(Exception):
            worker._execute_task()

    @patch('requests.get')
    def test__execute_task__not_downloadable(self, mock_get):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        
        # Mock requests.get to return non-200
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception):
            worker._execute_task()

    @patch('requests.post')
    @patch('requests.get')
    def test__execute_task__error_in_img_extraction(self, mock_get, mock_post):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        
        # mock pdf download success
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.content = b"fake_pdf"
        mock_get.return_value = mock_get_resp
        
        # mock post to identify_imgs to fail (non-200)
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 500
        mock_post.return_value = mock_post_resp
        
        with self.assertRaises(Exception):
            worker._execute_task()

    @patch('requests.post')
    @patch('requests.get')
    def test__execute_task__no_imgs_found(self, mock_get, mock_post):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        
        # mock pdf download success
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.content = b"fake_pdf"
        mock_get.return_value = mock_get_resp
        
        # mock identify_imgs success but no images found
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {"imgs": []}
        mock_post.return_value = mock_post_resp
        
        with self.assertRaises(Exception):
            worker._execute_task()

    @patch('requests.post')
    @patch('requests.get')
    def test__execute_task__valid(self, mock_get, mock_post):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        
        # mock pdf download success
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.content = b"fake_pdf"
        mock_get.return_value = mock_get_resp
        
        # mock identify_imgs and extract_img success
        mock_identify_resp = MagicMock()
        mock_identify_resp.status_code = 200
        mock_identify_resp.json.return_value = {"imgs": [{"page": 1, "startPos": {"x": 0, "y": 0}, "endPos": {"x": 5, "y": 10}}]}
        
        mock_extract_resp = MagicMock()
        mock_extract_resp.status_code = 200
        mock_extract_resp.content = b"fake_png_data"
        
        mock_post.side_effect = [mock_identify_resp, mock_extract_resp]
        
        worker._execute_task()
        self.assertEqual(len(worker._extracted_images), 1)
        self.assertEqual(worker._extracted_images[0]["border"]["page"], 1)

    def test__send_result__invalid_chemkg(self):
        worker = self.create_worker(MockChemKG_InvalidUrl, MockQueries)
        worker._publication_doi = publication_doi
        # Set up a fake image path to upload
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"data")
            filePath = f.name
            
        worker._extracted_images = [{"filePath": filePath, "border": {}}]
        
        try:
            with self.assertRaises(Exception):
                worker._send_result()
        finally:
            import os
            if os.path.exists(filePath):
                os.remove(filePath)

    def test__send_result__no_doi_set(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = None
        with self.assertRaises(Exception):
            worker._send_result()

    def test__send_result__no_images_to_upload(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        worker._extracted_images = []
        with self.assertRaises(Exception):
            worker._send_result()

    def test__send_result__upload_fails(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        
        # mock uploadFile to return failure dict
        worker._chemkg.uploadFile = MagicMock(return_value={"errors": [{"message": "failed"}]})
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"data")
            filePath = f.name
            
        worker._extracted_images = [{"filePath": filePath, "border": {}}]
        try:
            with self.assertRaises(Exception):
                worker._send_result()
        finally:
            import os
            if os.path.exists(filePath):
                os.remove(filePath)

    def test__send_result__valid(self):
        worker = self.create_worker(MockChemKG, MockQueries)
        worker._publication_doi = publication_doi
        
        # mock uploadFile to return success
        worker._chemkg.uploadFile = MagicMock(return_value={"data": {"uploadFile": {"fileURI": "http://uploaded.url"}}})
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"data")
            filePath = f.name
            
        worker._extracted_images = [{"filePath": filePath, "border": {}}]
        try:
            worker._send_result()
            worker._chemkg.uploadFile.assert_called_once_with(filePath, worker._publication_uri)
        finally:
            import os
            if os.path.exists(filePath):
                os.remove(filePath)

