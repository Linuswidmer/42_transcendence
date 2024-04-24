all: prod

prod: export LOCAL_IP = $(shell ifconfig | grep -A 1 'eno2' | tail -1 | awk '{ print $$2}')
prod: export LOCAL_IP_CSRF = https://$(shell ifconfig | grep -A 1 'eno2' | tail -1 | awk '{ print $$2}'):8443
prod: clean
	cd srcs && docker compose up --build

open: 
	export LOCAL_IP=$(shell ifconfig | grep -A 1 'eno2' | tail -1 | awk '{ print $$2}') && \
	xdg-open https://$$LOCAL_IP:8443/
	# does not work in all clusters, since the name of the network (eno2) is different

dev: clean
	make -C ./srcs/app_server dev

clean:
	-docker stop $(shell docker ps -aq)
	-docker rm $(shell docker ps -aq)

fclean: clean
	-docker rmi $(shell docker images -q)

setup:
	virtualenv venv
	. venv/bin/activate && pip install -r ./srcs/app_server/requirements.txt

flush_db:
	docker exec -it django python3 manage.py flush --no-input

re: fclean all