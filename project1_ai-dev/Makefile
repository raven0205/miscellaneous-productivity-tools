.PHONY: install run test docker-up docker-down

install:
	pip3 install -r requirements.txt

run:
	python3 app.py

test:
	python3 -m unittest discover tests

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
