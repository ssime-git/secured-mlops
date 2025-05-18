.PHONY: setup rebuild restart logs clean train test

setup:
	chmod +x setup.sh
	./setup.sh

rebuild:
	docker-compose down -v
	docker compose up --build -d

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	true

train:
	docker-compose exec code-server /usr/bin/python3 /config/workspace/train_model.py

test-connectivity:
	docker-compose exec code-server python3 /config/workspace/test_api_connection.py

test:
	docker-compose exec code-server /usr/bin/python3 /config/workspace/test_client.py