dev: clean
	make -C ./srcs/app_server dev

prod: clean
	cd srcs && docker compose up -d

clean:
	-docker stop $(shell docker ps -aq)
	-docker rm $(shell docker ps -aq)

setup:
	virtualenv venv
	. venv/bin/activate && pip install -r ./srcs/app_server/requirements.txt