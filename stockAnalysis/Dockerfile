FROM python:3.9-slim-buster

# setup environment variable
ENV DockerHOME=/src

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip

# copy whole project to your docker home directory.
COPY . $DockerHOME

# run this command to install all dependencies
RUN pip install -r requirements.txt

#CMD [ "python", "tables.py", "--host=0.0.0.0"]
#CMD python manage.py runserver --noreload

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000","--noreload"]