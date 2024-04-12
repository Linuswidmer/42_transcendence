dev: clean
	make -C ./srcs/app_server dev

prod: clean
	cd srcs && docker compose up --build

clean:
	-docker stop $(shell docker ps -aq)
	-docker rm $(shell docker ps -aq)

setup:
	virtualenv venv
	. venv/bin/activate && pip install -r ./srcs/app_server/requirements.txt

delete_db:
	docker exec -it django python3 manage.py flush --no-input