# The app explained simply

The app is a budget calculator for a football transfer plan. It is not a player ranking and not a prediction machine. You set the constraints, it scores the candidates, and it returns the best three player bundle it can defend.

## The one sentence to remember

"На входе бюджет, риск и веса, на выходе три игрока, которые закрывают три позиции и дают лучший баланс fit, value и safety."

## The three scores

Every candidate gets three scores from 0 to 100.

| Score | Plain meaning | How it is built |
|---|---|---|
| Fit | How closely the player matches the role | Kanté similarity for midfield, defensive profile for centre backs, box threat for forwards |
| Value | How cheap the player is against similar players | Local and global market value models. Positive gap means cheaper than expected |
| Safety | How available and low risk the player is | Minutes, injuries, age and cards |

The sidebar changes how much each score matters.

## The four sidebar controls

1. **Preference preset.** Recommended, Balanced, Value first, Quality first. It changes the weights of fit, value and safety.
2. **Transfer budget.** EUR 20m to 60m. The plan must fit under this number.
3. **Maximum risk.** Filters out fragile players.
4. **Maximum age.** Filters out older players.

The default is Recommended: 0.40 fit, 0.20 value, 0.40 safety, EUR 50m, risk 70, age 29.

## The five tabs

### Decision

This is the answer. It shows the current three player plan, the total fees, the budget left and the plan score. It also shows the alternatives and what happened to the recommended players after 2016.

### Squad need

This is the why. It shows Leicester's style fingerprint, Kanté's real match actions and his percentile ranks. The point is simple: Leicester needed a destroyer who could carry the ball, not a playmaker.

### Market

This is the pricing engine. The global model learns from 30,939 player seasons. The local model learns from the 2015/16 Premier League event data. The backtest shows whether the undervalued signal held.

### Shortlist

This is the workbench. The map shows fit against value, with point size as the fee. The table lists the candidates. Player detail shows the percentile bars. Plan builder lets you pick your own three players and see the score.

### Method

This is the defense page. It lists the data, the checks, the limitations and the AI use. Use it when someone asks how you avoided leakage or why market value is not a fee.

## The default plan

At the default settings the app recommends:

- Idrissa Gueye, central midfield, EUR 9m
- Steve Cook, centre back, EUR 3m
- Odion Ighalo, centre forward, EUR 12m

Total: EUR 24m. Left: EUR 26m.

Why:

- Gueye is the closest real match replacement for Kanté. He is not a bargain, and the app says so.
- Cook is the value pick. The model sees a large gap between his price and similar defenders.
- Ighalo is the box threat. 15 goals, 16.9 xG, EUR 12m.

## What changes when you move the controls

- **Balanced preset.** Coquelin, Cook, Ighalo, EUR 27m. Coquelin has a better value score than Gueye.
- **Quality first preset.** Gueye, Funes Mori, Ighalo, EUR 31m. More weight on fit.
- **Value first preset.** Coquelin, Cook, Ighalo, EUR 27m. Coquelin's market gap wins.
- **Budget 30.** The plan still fits. The recommended plan is EUR 24m.
- **Budget 20.** Fewer needs can be filled. The app will relax the requirement to fill all three.
- **Risk 45.** Fragile players disappear from the shortlist.

This is the best answer to "is the app dynamic?". Change the weights or the budget, and the plan changes.

## A 60 second demo

Open http://localhost:8501 and say:

"Это калькулятор трансферного плана. Для каждого игрока считаются три оценки: fit, насколько он подходит под роль, value, насколько он дешёвый относительно рынка, и safety, насколько он доступен. В сайдбаре я задаю бюджет, риск, возраст и веса. Оптимизатор выбирает по одному игроку на каждую позицию. По умолчанию выходит Гейе, Кук и Игало за 24 миллиона. Если поставить Value first, выходит Коклен вместо Гейе. Если Budget 30, план всё ещё помещается. Приложение показывает не просто список, а конкретный план под ограничения."

Then click:

1. Decision tab, point at the three cards.
2. Preset Value first, point at Coquelin.
3. Preset Recommended, budget 30, point at the same plan and the leftover.
4. Shortlist tab, point at Gueye at the top of fit and Cook at the far right of value.
5. Method tab, point at the limitations.

## Defense answers in one line

**Why not the most expensive player?**
Price is not fit. The model separates what the market pays from what the team needs.

**Why Gueye if the value model does not call him cheap?**
The market underprices defensive actions. Gueye is the closest profile, and Cook carries the value case.

**Why not van Dijk?**
Higher ceiling, but EUR 9m more and the fit score is not better enough for the recommended plan.

**How did you avoid leakage?**
Cutoff 1 July 2016, features known during the season, future season holdout and out of fold predictions.

**What is the biggest limitation?**
One league of event data, market value as a fee proxy and a retrospective case. The report states all three.

**Why does the plan change when I move a slider?**
The weights and constraints are explicit. The optimiser returns the best bundle for those settings, not a fixed answer.

## What not to say

- Do not say Gueye is a bargain. The model says he is fairly priced.
- Do not say the backtest guarantees the future. It is a check, not a promise.
- Do not say the model understands football. It learns market prices and event profiles.
- Do not say the app is deployed if it is running locally. Say it runs on Streamlit locally.

## The three sentence version

"The app is a decision support tool for a transfer window. It scores every candidate on fit, value and safety, then solves a budget constrained plan with one player per need. The default plan is Gueye, Cook and Ighalo for EUR 24m, and the report shows the validation, the alternatives and the risks."
