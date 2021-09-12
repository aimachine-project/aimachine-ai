FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt install -y \
python3 \
python3-dev \
pip \
nano \
sudo


RUN useradd --create-home --shell /bin/bash aimachine && usermod -aG sudo aimachine

WORKDIR /home/aimachine

COPY requirements.txt aimachine/*.py ./aimachine/

RUN pip install -r requirements.txt

