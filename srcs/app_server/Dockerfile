FROM ubuntu:latest

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install x11
RUN apt-get update && apt-get install -qqy x11-apps

# install python and pip
RUN apt-get install -y python3 python3-pip

# upgrade pip
RUN pip3 install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip3 install --no-cache-dir -r requirements.txt

#entry point file
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./create_default_users.py /usr/src/app/create_default_users.py

COPY . /usr/src/app

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]