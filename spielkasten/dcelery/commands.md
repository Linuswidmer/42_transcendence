## setup and run venv
virtuelenv venv
source venv/bin/activate

## Requirements
pip freeze > requirements.txt


## Docker
docker-compose up -d --build
docker rmi -f $(docker images -a -q)
