FROM python:3.10-alpine

WORKDIR /source

COPY . .

RUN pip install -r requirements.txt

CMD [ "python", "./source/wsgi.py"]
