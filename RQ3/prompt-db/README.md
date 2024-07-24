# Red Team Prompt Database

Stores the prompts created by the testers. Saves them to a Postgres database. Uses Docker. Data is persisted in the `postgres_data` directory (as a volume).

## Run

```bash
docker compose up -d
```

## Cleanup

```bash
docker compose down
rm -rf postgres_data
```
