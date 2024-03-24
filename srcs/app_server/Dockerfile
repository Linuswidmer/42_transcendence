#leon: i changed the image, in order to get pygame working (+pygame added to requirements.txt)
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

COPY . /usr/src/app

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]