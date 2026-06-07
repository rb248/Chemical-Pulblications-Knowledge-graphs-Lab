FROM pytorch/pytorch:latest
WORKDIR /code

COPY ./docker/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./docker/vgg16.py /code/vgg16.py
COPY ./docker/layout_parser.py /code/layout_parser.py

EXPOSE 8080
CMD ['python','vgg16.py']
CMD ['python','layout_parser.py']

# copy all files from current working directory to image
COPY ./app /code/app

# set up FastAPI
CMD ["uvicorn", "app.main:application", "--host", "0.0.0.0", "--port", "80"]
