import json
import os
import tempfile
import requests
from json import JSONDecodeError

from kgtool.interface import ChemKG
from requests.exceptions import InvalidSchema

from services.abstract_worker import Worker
from services.img_extraction.extraction_queries import Queries


class ExtractionWorker(Worker):

    def __init__(self, api_url="http://127.0.0.1:8080"):
        super().__init__()
        kg_url = os.getenv("KG_URL", "http://h3008088.stratoserver.net:4001/graphql")
        kg_graph = os.getenv("KG_GRAPH", "KGlab")
        self._chemkg = ChemKG(url=kg_url, graph=kg_graph)
        self._publication_doi = None
        self._publication_uri = None
        self._queries = Queries()
        self._api_url = api_url
        self._extracted_images = []
        self._temp_dir = None

    @classmethod
    def asWorker(cls):
        return cls()

    def _ask_for_task(self):
        """
        Consult the ChemEngKG to get a publication without assigned figures, save a publication without assigned figures.
        - Returns whether a publication without assigned figures exists or not
        """
        try:
            query_result = self._chemkg.runSparql(self._queries.get_some_publication_wo_img())['data']['runSparql']
            data = json.loads(query_result)['results']['bindings']
        except (InvalidSchema, JSONDecodeError, KeyError):
            # Unexpected Exception
            raise Exception("A problem with the query occurred: internal error, fix query or connection to KG")  # TODO: exception handling

        try:
            to_be_handled_report = data[0]
        except IndexError:
            # "Expected" exception -> can happen
            self._publication_doi = None
            return False  # No publication without assigned images exists

        try:
            self._publication_doi = to_be_handled_report['doi']['value']
        except KeyError:
            # Unexpected Exception
            raise Exception("A problem with the query occurred: internal error, fix query or connection to KG")  # TODO: exception handling
        # TODO question: Need to check whether download URL exists? Or can be assumed?
        return True

    def _execute_task(self):
        """
        Execute the task setup by **ask_for_task**:
        - get the publication pdf
        - extract images from the publication, save them
        """
        if self._publication_doi is None:
            # Unexpected Exception
            raise Exception("No task was not set -> internal error, fix setting task")  # TODO: exception handling
        try:
            query_result = self._chemkg.runSparql(self._queries.get_download_link_with_given_doi(self._publication_doi))['data']['runSparql']
            data = json.loads(query_result)['results']['bindings']
        except (InvalidSchema, JSONDecodeError, KeyError):
            # Unexpected Exception
            raise Exception("A problem with the query occurred: internal error, fix query or connection to KG")  # TODO: exception handling

        doi_retrieved = None
        download_url = None
        for binding in data:
            if 'doi' in binding:
                doi_retrieved = binding['doi']['value']
            if 'downloadURL' in binding:
                download_url = binding['downloadURL']['value']
            if 'article' in binding:
                self._publication_uri = binding['article']['value']

        if doi_retrieved is None or download_url is None:
            raise Exception("Query response was missing required fields 'doi' or 'downloadURL'.")

        if self._publication_uri is None:
            self._publication_uri = f"http://doi.org/{self._publication_doi}"

        if doi_retrieved != self._publication_doi:
            raise Exception(f"Query returned unexpected DOI: {doi_retrieved}, expected {self._publication_doi}.")

        # Download the PDF
        try:
            response = requests.get(download_url, timeout=10)
            if response.status_code != 200:
                raise Exception("Failed to download PDF: status code not 200.")
            pdf_content = response.content
        except Exception as e:
            raise Exception(f"Failed to download PDF: {str(e)}")

        # Call the Image Extraction API to identify images
        try:
            files = {"pdf_file": ("paper.pdf", pdf_content, "application/pdf")}
            identify_response = requests.post(f"{self._api_url}/img_detection/identify_imgs", files=files, timeout=30)
            if identify_response.status_code != 200:
                raise Exception("Failed to identify images in PDF: status code not 200.")
            borders_data = identify_response.json()
        except Exception as e:
            raise Exception(f"Error during image identification: {str(e)}")

        imgs = borders_data.get('imgs', [])
        if not imgs:
            raise Exception("No images found in the PDF.")

        # Create temporary directory to store files
        self._temp_dir = tempfile.TemporaryDirectory()
        self._extracted_images = []

        # Extract each image
        for idx, border in enumerate(imgs):
            try:
                extract_response = requests.post(
                    f"{self._api_url}/img_detection/extract_img",
                    files={"pdf_file": ("paper.pdf", pdf_content, "application/pdf")},
                    data={"img_border": json.dumps(border)},
                    timeout=30
                )
                if extract_response.status_code != 200:
                    raise Exception("Failed to extract image cutout: status code not 200.")
                
                temp_file_path = os.path.join(self._temp_dir.name, f"extracted_img_{idx}.png")
                with open(temp_file_path, "wb") as f:
                    f.write(extract_response.content)

                self._extracted_images.append({
                    "filePath": temp_file_path,
                    "border": border
                })
            except Exception as e:
                raise Exception(f"Error during image extraction: {str(e)}")

    def _send_result(self):
        """
        Send the results from **execute_task** to the ChemEngKG:
        - upload the extracted images to the corresponding publication
        """
        if self._publication_doi is None:
            raise Exception("No DOI set -> cannot send result.")

        if not self._extracted_images:
            raise Exception("No images to upload.")

        for img_info in self._extracted_images:
            file_path = img_info["filePath"]
            try:
                response = self._chemkg.uploadFile(file_path, self._publication_uri)
                if not response or 'errors' in response or 'data' not in response or not response['data'].get('uploadFile'):
                    raise Exception(f"Upload failed: {response}")
            except Exception as e:
                raise Exception(f"Failed to upload image file {file_path} to KG: {str(e)}")

        # Clean up temporary directory
        if self._temp_dir is not None:
            try:
                self._temp_dir.cleanup()
            except Exception:
                pass

    def run_worker(self):
        # What kind of error should be raised, if no task found
        if not self._ask_for_task():
            # Expected exception: need to be handled by the worker caller
            raise Exception("No publication without images was found -> no task to fulfill")  # TODO: exception handling
        self._execute_task()
        self._send_result()


if __name__ == '__main__':
    worker = ExtractionWorker()
    worker.run_worker()
