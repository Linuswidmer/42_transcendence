dev: clean
	make -C ./srcs/app_server dev

prod: clean
	cd srcs && docker compose up --build

clean:
	-docker stop $(shell docker ps -aq)
	-docker rm $(shell docker ps -aq)

setup:
#	python3 -m venv venv
#	. venv/bin/activate && pip install -r ./srcs/app_server/requirements.txt
	virtualenv venv
	. venv/bin/activate && pip install -r ./srcs/app_server/requirements.txt