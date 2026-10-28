# Short scripts

Full version: [SPEAKER_SCRIPT.md](SPEAKER_SCRIPT.md)

Slides are in English. Use the English lines as written, or translate them live. Keep the numbers unchanged.

## Что есть что, по-русски

- **Приложение**: калькулятор трансферного плана, не рейтинг игроков.
- **Fit**: насколько игрок подходит под роль. Для полузащиты это сходство с Канте по реальным действиям.
- **Value**: насколько игрок дешёвый относительно похожих игроков по рынку.
- **Safety**: насколько игрок доступен. Минуты, травмы, возраст, карточки.
- **Сайдбар**: задаёт приоритеты и ограничения. Preset меняет веса, budget задаёт деньги, risk и age фильтруют пул.
- **Оптимизатор**: выбирает по одному игроку на CM, CB и ST так, чтобы сумма взвешенных оценок была максимальной и гонорары помещались в бюджет.

## Что меняется в сайдбаре

| Контрол | Что происходит | Пример |
|---|---|---|
| Preset | Меняются веса fit, value, safety | Recommended: Гейе, Кук, Игало. Value first: Коклен, Кук, Игало. Quality first: Гейе, Фунес Мори, Игало |
| Budget | Отсекает слишком дорогие планы | 24-60m: тот же план. 20m: Кук, Ромеу, Игало |
| Risk | Фильтрует шортлист | 20-90: план тот же, потому что выбранные игроки уже безопасны |
| Age | Отсекает возрастных игроков | 27: Кинг вместо Игало. 25: ван Дейк, Эмре Джан, Кинг. 24: Мбемба, Эмре Джан, Митрович |

## Dinmukhammed, slides 1 to 4

**Slide 1**

"We are Dinmukhammed, Laura and Zhaidar, AAI-2504M. Our question is how to replace Kanté with a EUR 50m budget and keep Leicester's identity. Our answer is Gueye, Cook and Ighalo for EUR 24m."

**Slide 2**

"This is a portfolio, not a ranking. Gueye for EUR 9m, Cook for EUR 3m, Ighalo for EUR 12m. Total EUR 24m, with EUR 26m left. Gueye is the fit, Cook is the value, Ighalo is the box threat."

**Slide 3**

"We use 380 Premier League matches from StatsBomb and 30,939 player seasons from Transfermarkt. The cutoff is 1 July 2016. The pipeline is parse, profile, price, score and optimise. Future values are used only for validation."

**Slide 4**

"Leicester had 42.6% possession and the lowest pass completion in the league, but 1.74 xG per match. Kanté made 1,594 defensive actions and 545 progressive passes and carries. They needed a destroyer, not a playmaker. Laura will show how we measured it."

## Laura, slides 5 to 7

**Slide 5**

"Kanté is 100th percentile for ball winning, recoveries, tackles and interceptions, but only 54th for pass completion. Our similarity score puts Gueye first at 0.93. Ramsey is at zero, because the label says defensive midfielder but the actions do not."

**Slide 6**

"The global model gets R2 0.734 and Spearman 0.855 on future seasons. The local model gets R2 0.614 against 0.495 for the baseline. The market pays for passing and attacking output, not for defensive actions. That is why Gueye can be the best fit and still look fairly priced."

**Slide 7**

"Undervalued players gained 11.8% over two years, the rest lost 10.9%. The hit rate was 52.8% against 35.8%. The global model beat the rest in all 10 evaluation seasons on a relative basis. It is a modest edge, not a guarantee."

## Zhaidar, slides 8 to 10

**Slide 8**

"Each candidate gets fit, value and safety. Fit is the role, value is the market gap, safety is availability. Gueye is the fit extreme, Cook is the value extreme, Coquelin is the balance at 81 fit and 82 value for EUR 12m."

**Slide 9**

"The recommended plan is Gueye, Cook and Ighalo for EUR 24m. It is the safety first optimum: 40% fit, 20% value, 40% safety. Coquelin is the value alternative, van Dijk the higher ceiling, Deeney the cheaper striker. The backtest gives +52%, with two hits and one miss."

**Slide 10**

"The risks are Gueye's passing, Cook's step up, Ighalo's one season and the pressing work. If the budget falls 20%, the plan still fits at EUR 24m. The limitations are one league, market value as a fee proxy and the retrospective case."

## Dinmukhammed, slide 11

**Slide 11**

"This is a decision system, not a black box. The data and code are public, the weights are explicit, and nine tests pass. The optimiser matches a brute force check. Thank you. We are happy to take questions."

## 60 second app demo, по-русски

"Это калькулятор трансферного плана. Для каждого игрока считаются три оценки: fit, value и safety. В сайдбаре я задаю бюджет, риск, возраст и веса. Оптимизатор выбирает по одному игроку на каждую позицию. По умолчанию выходит Гейе, Кук и Игало за 24 миллиона. Если поставить Value first, выходит Коклен вместо Гейе. Если поставить возраст 27, выходит Кинг вместо Игало. Приложение показывает не список, а конкретный план под ограничения."

## Five answers, one line each

- **Why not the most expensive player?** Price is not fit.
- **Why Gueye if the value model does not call him cheap?** The market underprices defensive actions, and Cook carries the value case.
- **Why not van Dijk?** Higher ceiling, but EUR 9m more and the fit score is not better enough for the recommended plan.
- **How did you avoid leakage?** Cutoff, features known during the season, future season holdout and out of fold predictions.
- **What is the biggest limitation?** One league of event data, market value as a fee proxy and a retrospective case.
