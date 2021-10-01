FROM ubuntu:focal

MAINTAINER Sebastian Syska (syska.seb@gmail.com)

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt install -y \
python3 \
python3-dev \
pip \
nano \
sudo

COPY requirements.txt aimachine/*.py ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python3","server.py"]
