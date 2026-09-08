# Порядок реализации (после approve Gherkin)

Не начинать, пока пользователь не утвердит `docs/features/*.feature`.

1. Bootstrap Next **16.3.x** + Tailwind **4.3** + React Compiler по [stack.md](./stack.md).
2. `globals.css` токены + layout шрифты (Geist + JetBrains_Mono).
3. `src/lib/scores/*` + Vitest на формулы и renormalize факторов.
4. `scripts/seed_synthetic.ts` → `data/synthetic/` + тест воспроизводимости и корреляций.
5. `MockWearableAdapter` + `TerraWearableAdapter` + factory.
6. Team Overview RSC + фильтры URL.
7. Athlete Detail + Recharts + heatmap.
8. Injury drawer.
9. Python stubs в `data/adapters` и `ml/models`.
10. Браузер: обзор → карточка → риск → пустой фильтр → «нет данных».

Quality-gates (workflow-orchestrator) — если пользователь не написал `skip gates`.
