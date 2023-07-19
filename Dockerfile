FROM python:3.9-slim-buster
# FROM python:3.8-alpine
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python", "tables.py", "--host=0.0.0.0"]