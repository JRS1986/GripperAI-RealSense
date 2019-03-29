# Dockerfile
FROM ubuntu:18.04
#FROM python:3-alpine sadly this makes some installs in 'pip install requirements' broken... should be somehow possible, but i just dont know how right now
#RUN apk add python2
#RUN apk add py2-pip

RUN apt-get update # update the package manager
RUN apt-get install -y python # install python
RUN apt-get install -y python3 # install python
RUN apt-get install -y python-pip
RUN apt-get install -y python3-pip

WORKDIR /app

COPY timezonescript.sh /app/timezonescript.sh
RUN /app/timezonescript.sh
RUN apt-get install -y python-tk

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
RUN pip3 install -r requirements.txt


COPY . /app
#COPY GripperViewer app/GripperViewer
#COPY gqcnn_jeffbranch_adapted app/gqcnn_jeffbranch_adapted


EXPOSE 80

#CMD ["python", "GripperViewer/main_uic.py"]
#RUN apt-get install -y python-pip python-dev build-essential # install pip other basic python libraries for building packages
#RUN pip install flask # install flask with pip
