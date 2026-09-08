# Digital Athlete Twin

Операционный дашборд готовности (водное поло). UI — Next.js на **localhost:3400**. Данные — Postgres + API в Docker.

## Запуск

```bash
docker compose up --build -d
npm run dev
```

- UI: http://localhost:3400
- API: http://localhost:8080/health
- Postgres: localhost:5432 (`sport` / `sport` / `athlete_twin`)

Сид в контейнере `seed` пишет 25 атлетов в БД. Фронт мок JSON не читает.

Стек UI: Next.js 16, Astryx (`theme-neutral`, light), Recharts, Motion.
