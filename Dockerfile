FROM python:3.8-slim-buster
#
# https://docs.docker.com/language/python/build-images/
#

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN rm -f .env

ENTRYPOINT ["python3", "iobtaiadapter.py"]

# sudo docker build -t iobtaiadapter -f Dockerfile  .
# sudo docker run -t --rm --privileged -v /dev:/dev --env-file ./.env --name iobtaiadapter iobtaiadapter
# sudo docker exec -it iobtaiadapter /bin/bash
# sudo docker container stop iobtaiadapter
# sudo docker tag iobtaiadapter iobtassets.azurecr.io/iobtaiadapter:v1.0.0
# sudo docker push iobtassets.azurecr.io/iobtaiadapter:v1.0.0
# sudo docker-compose -f txrx-docker-compose.yml up
# sudo docker-compose -f txrx-docker-compose.yml down
# az login
# az acr login --name iobtassets
