dev:
	make -C ./srcs/app_server dev

prod:
	-docker stop $(shell docker ps -aq)
	-docker rm $(shell docker ps -aq)
	cd srcs && docker compose up --build

down:
	cd srcs && docker compose down

setup:
	virtualenv venv && . venv/bin/activate
	pip install -r ./srcs/app_server/requirements.txt
