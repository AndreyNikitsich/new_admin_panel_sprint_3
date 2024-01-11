# ETL Service
Load movies from Postgres to Elasticsearch

## Local development
```bash
cp .env.example .env  # edit if necessary
docker-compose up
```

## Start on production
```bash
cp .env.example .env  # edit if necessary
docker-compose -f docker-compose-prod.yml up
```

## Admin Panel with Postgres
[Admin panel repo](https://github.com/AndreyNikitsich/new_admin_panel_sprint_2) use the same docker network as ETL. Just download repo and follow instruction in README.md before run ETL