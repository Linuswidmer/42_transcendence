dev:
	make -C ./srcs/app_server dev

prod:
	cd srcs && docker compose up --build

down:
	cd srcs && docker compose down

setup:
#	python3 -m venv venv
#	. venv/bin/activate && pip install -r ./srcs/app_server/requirements.txt

#setup:
	virtualenv venv && . venv/bin/activate
	pip install -r ./srcs/app_server/requirements.txt
