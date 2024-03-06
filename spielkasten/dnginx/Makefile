dev:
	make -C ./dnginx

prod:
	docker compose up --build

clean:
	docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker rmi $(docker images -q)
