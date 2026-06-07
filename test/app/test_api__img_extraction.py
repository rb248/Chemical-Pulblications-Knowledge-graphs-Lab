import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.img_extraction import router
from app.schemes import ModelInfo, ImageBorders, ImageBorder, PositionOnPage


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        yield client


def test__get_info_for_img_extraction(client):
    endpoint = '/img_detection/info'
    response = client.get(endpoint)

    # validate: correct status code and data format
    assert response.status_code == 200
    assert isinstance(ModelInfo.parse_obj(response.json()), ModelInfo)

    # validate: getting same response data when calling endpoint twice
    snd_response = client.get('/img_detection/info')
    assert response.json() == snd_response.json()


# def test__classify_img__valid_input(client):
#     endpoint = '/img_classification/get_class'
#
#     filename = './test/assets/test_img.png'
#     response = client.post(endpoint, files={"img_file": open(filename, "rb")})
#
#     assert response.status_code == 200
#
#     expected_response = ImageClassificationResponse(classes=[
#         ImageClassificationResult(class_name="cat", confidence=0.98)
#     ])
#     assert response.json() == expected_response.dict()


def test__identify_imgs_in_pdf__valid_input(client):
    endpoint = '/img_detection/identify_imgs'

    filename = './test/assets/test_paper.pdf'
    response = client.post(endpoint, files={"pdf_file": open(filename, "rb")})

    assert response.status_code == 200

    # TODO: put in result that makes sense -> maybe number of images detected?
    expected_response = ImageBorders(imgs=[
        ImageBorder(
            page=1,
            startPos=PositionOnPage(x=0, y=0),
            endPos=PositionOnPage(x=5, y=10)
        )
    ])
    assert response.json() == expected_response.dict()


def test__identify_imgs_in_pdf__wrong_input(client):
    endpoint = '/img_detection/identify_imgs'

    filename = './test/assets/test_img.png'
    response = client.post(endpoint, files={"pdf_file": open(filename, "rb")})

    assert response.status_code == 400


def test__cut_out_img_in_pdf__valid_input(client):
    endpoint = '/img_detection/extract_img'

    filename = './test/assets/test_paper.pdf'
    response = client.post(endpoint,
                           files={"pdf_file": open(filename, "rb")},
                           data={"img_border": '{"page": 1, "startPos": {"x": 10, "y": 10}, "endPos": {"x": 100, "y": 100}}'})

    assert response.status_code == 200

    # Assert that the response has the correct content type
    assert response.headers["content-type"] == "application/octet-stream"

    # Assert that the response contains the file content
    assert response.content


def test__cut_out_img_in_pdf__wrong_input(client):
    endpoint = '/img_detection/extract_img'

    filename = './test/assets/test_img.png'
    response = client.post(endpoint,
                           files={"pdf_file": open(filename, "rb")},
                           data={"img_border": '{"page": 1, "startPos": {"x": 10, "y": 10}, "endPos": {"x": 100, "y": 100}}'})

    assert response.status_code == 400
