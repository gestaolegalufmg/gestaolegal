run:
	docker-compose --project-name development up

run_production:
	docker-compose --project-name production -f docker-compose.yml -f docker-compose.prod.yml up -d

run_test:
	docker-compose --project-name test docker-compose.test.yml up -d

stop:
	docker stop app_gl db_gl adminer_gl