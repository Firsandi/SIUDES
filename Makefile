.PHONY: up down logs migrate seed test-load

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=50

migrate:
	docker compose exec unit-service php artisan migrate

seed:
	docker compose exec unit-service php artisan db:seed

test-load:
	docker compose run --rm locust -f /mnt/locust/locustfile.py --host=http://nginx