import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.img_classification import router
from app.schemes import ModelInfo, ImageClassificationResponse, ImageClassificationResult


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        yield client


def test__get_info_for_img_classification(client):
    endpoint = '/img_classification/info'
    response = client.get(endpoint)

    # validate: correct status code and data format
    assert response.status_code == 200
    assert isinstance(ModelInfo.parse_obj(response.json()), ModelInfo)

    # validate: getting same response data when calling endpoint twice
    snd_response = client.get('/img_classification/info')
    assert response.json() == snd_response.json()


def test__classify_img__valid_input(client):
    endpoint = '/img_classification/get_class'

    filename = './test/assets/test_img.png'
    response = client.post(endpoint, files={"img_file": open(filename, "rb")})

    assert response.status_code == 200

    # TODO: put in result that makes sense -> maybe set of possible classes?
    expected_response = ImageClassificationResponse(classes=[
        ImageClassificationResult(class_name="cat", confidence=0.98)
    ])
    assert response.json() == expected_response.dict()


def test__classify_img__wrong_input(client):
    endpoint = '/img_classification/get_class'

    filename = './test/assets/test_img_wrong_type.jpg'
    response = client.post(endpoint, files={"img_file": open(filename, "rb")})

    assert response.status_code == 400
