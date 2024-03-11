dev:
	make -C ./srcs/app_server dev

prod:
	cd srcs && docker compose up --build

down:
	cd srcs && docker compose down

setup:
	virtualenv venv && . venv/bin/activate
	pip install -r ./srcs/app_server/requirements.txt
