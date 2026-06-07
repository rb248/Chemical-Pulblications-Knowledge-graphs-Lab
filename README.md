# ModelZoo
Contains different machine learning models for chemical engineering and makes them available via a restful API.

The docker image can be build locally and then started locally by executing
```commandline
docker build -t kglab-model-zoo .
docker run -d --name kglab -p 80:80 kglab-model-zoo
```
The API can then be reached through `http://localhost:80/`

## API

### ./app/main.py

FastAPI executing the models.

For a detailed documentation of the endpoints: see the openapi endpoint `<host>:<port>/documentation`
- The opened SwaggerUI can also be utilized to directly test the endpoints

## Models
Inside the `./app/models` folder

### SMILES to Property Transformer

> NOTE: Not supported (code can be found in directory `old_app`, but is not integrated in the build docker) 

Code copied from the repository [here](https://github.com/Bene94/SMILES2PropertiesTransformer) from the paper "A SMILE is all you need: Predicting limiting  activity coefficients from SMILES with natural language processing" ([here](https://arxiv.org/abs/2206.07048)) by Winter et al.

Minor adjustments:

- https://github.com/process-intelligence-research/ModelAPI/blob/main/SMILES2PropertiesTransformer/src/misc/simple_evaluation.py
  - Turn module into executable function.
- https://github.com/process-intelligence-research/ModelAPI/blob/main/SMILES2PropertiesTransformer/src/transprop/load_model.py
  - add arg to function load_model to choose PyTorch device (CPU vs GPU)

### Flowsheet recognition classifying images

Code copied from [here](https://drive.google.com/file/d/1ahO7mpRKNW00YmCCIGJgPxUAkLoXj6z8/view?usp=sharing), concrete architecture captured in the paper ["Flowsheet Recognition using Deep Convolutional Neural Networks"](https://doi.org/10.1016/B978-0-323-85159-6.50261-X) by Schulze Balhorn, Gao, Goldstein, and Schweidtmann.

### Object detection extracting figures from documents

Code copied from [here](https://drive.google.com/file/d/1HLQrLQTv-1PU2iLfnKCg0YXmx7Y7278q/view?usp=sharing) using the Python package [Layout Parser](https://layout-parser.github.io/) (detailed documentation [here](https://layout-parser.readthedocs.io/en/latest/notes/installation.html)).

## Testing and CI

There are two workflows executed whenever pushing to the repository. 
- One is for testing whether the docker container function properly (can be build), defined in `push.yml`
- The other is for executing the unit tests defined under `./test` and checking whether they run through smoothly, defined in `unit_test.yml`

### Unit tests
The unit tests are implemented for the following elements:
- The API for object detection and image classification

They can be executed by running `pytest` or `python -m unittest` in the working directory of this project. To check the code coverage of the tests, the following commands can be used:
```commandline
  % First of all: package `coverage` must be installed -> run
  pip install coverage
  
  % If the package is installed, run the following commands to get the coverage report and an html output for seeing which parts of the code where tested
  python -m coverage run -m unittest
  python -m coverage report
  python -m coverage html 
```

## Documentation
A detailed explanation for the endpoints can be seen under the endpoint `<host>:<port>/documentation`
- This endpoint provides the [Swagger](https://github.com/swagger-api/swagger-ui) documentation (also called OpenAPI)

# Microservices
Additionally to the models and the according API, this repository also contains microservices to execute the models.
- They are all implementing a so called `worker` (see `services/abstract_worker.py`)

They are located in the module `services`.
- The unit tests are also executed with the test command from above, the tests are located in `test/services`

## Image Extraction
The task is to:
1. Fetch a publication from the knowledge graph (ChemKG) that doesn't have any images assigned yet.
2. Extract images from that publication.
3. Post the images to the knowledge graph.
