# Стек и версии

Снимок реестров **2026-09-08**. При установке брать `@latest` / текущий PyPI latest; не фиксировать Next 14/15.

## Runtime

| Среда | Минимум | На машине разработки |
|-------|---------|----------------------|
| Node.js | 20.9+ (требование Next 16) | 22 LTS предпочтительно |
| Python | 3.13+ | 3.13.7 |

## JavaScript (npm latest на дату снимка)

| Пакет | Latest | Зачем |
|-------|--------|--------|
| `next` | **16.3.4** | App Router, Turbopack по умолчанию, React Compiler |
| `react` / `react-dom` | **19.2.8** | RSC + 19.2 |
| `typescript` | **7.0.2** | Next 16 требует TS 5.1+; ставить current 7 |
| `@types/react` | **19.2.18** | |
| `@types/node` | **26.5.0** | |
| `tailwindcss` | **4.3.3** | CSS-first `@theme` |
| `@tailwindcss/postcss` | **4.3.3** | PostCSS-плагин v4 |
| `postcss` | **8.5.28** | |
| `recharts` | **3.10.1** | Line chart + zone bands |
| `motion` | **13.2.0** | `import { motion } from "motion/react"` |
| `eslint` | **10.10.0** | |
| `eslint-config-next` | **16.3.4** | совпадает с major Next |
| `babel-plugin-react-compiler` | **1.0.0** | стабильный compiler в Next 16 |
| `zod` | **4.5.4** | валидация снимка адаптера |
| `tsx` | **4.23.13** | запуск `scripts/seed_synthetic.ts` |
| `vitest` | **5.0.0** | тесты seed/score/adapter |
| `clsx` | **2.1.1** | склейка className без cva/shadcn |

Не ставить: `framer-motion`, `chart.js` / `react-chartjs-2`, `shadcn/ui` как дефолтный kit, Inter как UI-шрифт.

**Шрифты:** `Geist` и `JetBrains_Mono` из `next/font/google`. Шаблон create-next-app даёт Geist_Mono — **заменить** на JetBrains_Mono для `tabular-nums`.

**Visx:** `@visx/xychart` latest 4.0.0. В MVP не подключать, пока Recharts 3 закрывает зоны и серии. Смена библиотеки не должна трогать адаптер.

## Python (PyPI latest на дату снимка)

| Пакет | Latest | Зачем |
|-------|--------|--------|
| pandas | 3.0.5 | loader / parquet |
| numpy | 2.5.3 | seed-корреляции, если seed на Python |
| scikit-learn | 1.9.0 | API бейзлайна, обучение на синтетике позже |
| pyarrow | 25.0.1 | parquet |
| pydantic | 2.13.5 | зеркало схемы DailyPhysio |

`kaggle` CLI — не в дефолтных deps. Добавлять только когда пользователь дал ключ.

NeuroKit2 — не в `requirements` этого прохода (см. `ml/notebooks/hrv-neurokit2-stub.md`).

## Bootstrap (после approve Gherkin)

Репозиторий уже содержит `app/` и `src/`. Не создавать вложенный проект.

```bash
npx create-next-app@latest . --typescript --tailwind --eslint --app --react-compiler --use-npm --import-alias "@/*"
```

Флаги: **не** `--src-dir` (маршруты уже в корневом `app/`). Если CLI откажется из-за непустой папки — поставить пакеты вручную:

```bash
npm i next@latest react@latest react-dom@latest recharts@latest motion@latest zod@latest clsx@latest
npm i -D typescript@latest @types/react@latest @types/node@latest tailwindcss@latest @tailwindcss/postcss@latest postcss@latest eslint@latest eslint-config-next@latest babel-plugin-react-compiler@latest tsx@latest vitest@latest
```

`next.config.ts`: `reactCompiler: true`. Не включать `middleware`. Turbopack не отключать.

## Next.js 16 — обязательные отличия от брифа «14+»

- `next build` **не** гоняет lint сам; lint — отдельный npm-скрипт.
- Async `params` у `app/athletes/[id]/page.tsx`: `const { id } = await params`.
- Нет Pages Router.
- `proxy.ts` не нужен для MVP (нет auth).
