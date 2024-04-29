FROM ubuntu:latest

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install x11
RUN apt-get update && apt-get install -qqy x11-apps

# install python, pip and venv
RUN apt-get install -y python3 python3-pip python3-venv

# create a virtual environment and activate it
RUN python3 -m venv venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

# upgrade pip
RUN pip3 install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt

#entry point file
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./create_default_users.py /usr/src/app/create_default_users.py

COPY . /usr/src/app

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]