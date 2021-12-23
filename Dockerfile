FROM python:3.7.12-slim-buster

WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_lg

RUN mkdir /code/data
RUN mkdir /code/output

COPY main.py main.py

CMD ["python", "main.py"]