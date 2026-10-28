# Assignment 5 speaker script

Team: Dinmukhammed Mynzhassar, Laura Duisenova, Zhaidar Kairat, AAI-2504M

Format: 13 to 15 minutes, three speakers, one shared argument.

Slides are in English. If the room prefers Russian, translate the same script live and keep the numbers unchanged.

## Timing

| Time | Speaker | Slides | Content |
|---|---|---|---|
| 0:00 to 5:00 | Dinmukhammed | 1 to 4 | Problem, plan, data, Leicester style |
| 5:00 to 10:00 | Laura | 5 to 7 | Kanté profile, market models, backtest |
| 10:00 to 14:00 | Zhaidar | 8 to 10 | Shortlist, decision, risks |
| 14:00 to 15:00 | Dinmukhammed | 11 | Close, reproducibility, questions |

## How to use this script

- Do not read the slides. Use the script as a guide and keep the numbers exact.
- Each speaker owns one question block in the Q&A, but everyone should be able to answer the basic questions.
- Handoffs are part of the timing. Say the handoff line, then stop.
- Rehearse once with a timer. The cut points are 5:00 and 10:00, not "when I finish".

## Slide 1. Title

Speaker: Dinmukhammed, 0:00 to 0:45

"Good morning. We are Dinmukhammed, Laura and Zhaidar, all in AAI-2504M. Our project is a transfer decision system for Leicester City in the summer of 2016. The question is simple. How do you replace N'Golo Kanté with a EUR 50m budget and keep the identity of the team? Our answer is a three player plan: Idrissa Gueye, Steve Cook and Odion Ighalo for EUR 24m. I will cover the problem, the data and the style. Laura will cover the value models and the validation. Zhaidar will cover the shortlist and the decision."

## Slide 2. The decision

Speaker: Dinmukhammed, 0:45 to 2:00

"This is the plan. Gueye from Aston Villa for EUR 9m, Cook from AFC Bournemouth for EUR 3m, and Ighalo from Watford for EUR 12m. Total fees: EUR 24m. That leaves EUR 26m for wages, agent fees and a January buffer.

The important word is portfolio. We are not ranking players. We are choosing a bundle that fills three needs under one budget. Gueye is the closest replacement for Kanté. Cook is the value pick, a EUR 3m defender with a large market gap. Ighalo is the proven box threat. Two of the three are undervalued by our models. Gueye is not, and we say that openly."

## Slide 3. What the data can see

Speaker: Dinmukhammed, 2:00 to 3:30

"How did we get here? Two independent sources.

StatsBomb open data gives us all 380 Premier League matches of 2015/16, 10,385 player match rows and 548 players. Every pass, carry, shot, pressure and defensive action.

The Transfermarkt datalake gives us 30,939 top five league player seasons, market values, performances, transfers and injuries.

The cutoff is 1 July 2016. Everything used to make the decision is available at that date. The 2017 and 2018 values are only for the validation.

The pipeline has five steps: parse the events, build the profiles, price the market, score the fit, and solve the budget plan. Raw data is not committed. The download script and the processed tables make the result reproducible."

## Slide 4. What Leicester were

Speaker: Dinmukhammed, 3:30 to 5:00

"Leicester were not a possession team. 42.6% possession. 68% pass completion, the lowest in the division. But 1.74 xG per match, 15.1% of their xG from set pieces, and 9.2% from counterattacks. This is a low block, direct, high threat team.

The left panel shows where Kanté won the ball: 1,594 defensive actions across 37 matches. The right panel shows 545 progressive passes and carries.

He was not a playmaker. He was a destroyer who could carry the ball. That is the profile we have to replace.

Laura will show how we measured it and how we priced it."

## Slide 5. Kanté was not a playmaker

Speaker: Laura, 5:00 to 6:30

"Kanté is extreme. Among Premier League midfielders with at least 900 minutes, he is 100th percentile for ball winning, recoveries, tackles and interceptions. 98th for pressures. 72nd for progressive carries. He is only 54th for pass completion and 34th for progressive passes.

So we built a similarity score on ten actions per 90: ball winning, pressures, progressive passes, progressive carries, pass completion, recoveries, tackles, interceptions, xG and shots.

Gueye is first at 0.93 cosine similarity. Kirchhoff is 0.75. Wanyama is 0.70. Coquelin is 0.68.

Ramsey is about zero. That last number matters. The data lists Ramsey as a defensive midfielder, but he does not play like Kanté. The label is not the role."

## Slide 6. Two market models

Speaker: Laura, 6:30 to 8:15

"We used two value models.

The global model learns from 30,939 player seasons in the top five leagues from 2010/11 to 2024/25. It predicts log market value relative to the league median, so inflation and league level are removed. We train up to 2020/21 and test on 2021/22 to 2024/25. The LightGBM model gets R2 0.734, Spearman 0.855 and a log error of 0.488. The baseline is an R2 of 0.007.

The local model uses the 2015/16 Premier League and 31 event features. It gets R2 0.614 against 0.495 for a baseline that knows only age, minutes, role and club rank.

The local model also shows the market bias. Passing and attacking output have positive coefficients. Defensive actions have negative coefficients once position and possession are controlled. The market does not pay for what Kanté did. That is why Gueye can be the best fit and still not look cheap."

## Slide 7. The undervalued signal

Speaker: Laura, 8:15 to 10:00

"Is the value gap real?

We flag the bottom 20% of residuals within each position group as undervalued, and we follow their market value for two years.

The undervalued group gained 11.8% in median market value. The rest lost 10.9%. The hit rate was 52.8% against 35.8%. At three years the gap widens: +10.5% against -26.9%.

The global model beat the rest in all 10 evaluation seasons on a relative basis, although absolute values fell in several seasons.

This is a modest edge, not a guarantee. We show the misses, not only the hits. Zhaidar will show how we turned this into a plan."

## Slide 8. The shortlist

Speaker: Zhaidar, 10:00 to 11:30

"Every candidate gets three scores.

Fit is the tactical profile. Kanté similarity for midfield, defensive volume and progression for centre backs, box threat for forwards.

Value is the average of the local and global market gap percentiles.

Safety is the inverse of a risk score built from minutes, injuries, age and cards.

This map shows the trade off. Gueye is at the top of the fit axis. Cook is at the far right of the value axis. Coquelin sits in the middle: 81 fit, 82 value, EUR 12m.

The shortlist is not a single ranking. It is a surface of choices."

## Slide 9. The plan

Speaker: Zhaidar, 11:30 to 13:00

"The recommended plan is Gueye, Cook and Ighalo.

Gueye is 95 fit, 22 value, 91 safety, EUR 9m.
Cook is 57 fit, 100 value, 96 safety, EUR 3m.
Ighalo is 79 fit, 82 value, 96 safety, EUR 12m.

Total: EUR 24m.

Why this plan? It is the safety first optimum: 0.40 fit, 0.20 value, 0.40 safety. For a club that has just lost a unique midfielder, availability and fit matter more than a marginal bargain. The plan leaves EUR 26m for wages and a January buffer.

The alternatives are Coquelin for value, van Dijk for a higher ceiling, and Deeney for a cheaper striker.

What happened next is a backtest, not a promise. Gueye +80%. Cook +85%. Ighalo -23%. The plan +52% in total. Two hits and one miss."

## Slide 10. Risks and what would change

Speaker: Zhaidar, 13:00 to 14:00

"The risks are clear.

Gueye is a safe short passer, not a creative progressor.
Cook steps up from Bournemouth.
Ighalo may be a one season outlier.
The 4 4 2 pressing needs work.

If the budget falls 20%, the recommended plan still fits at EUR 24m. If it falls 40%, the base plan still fits at EUR 27m.

The limitations are one league of event data, market value as a fee proxy, a retrospective case and noisy residuals. The report states all of them.

The point is not to hide uncertainty. The point is to make the trade offs visible."

## Slide 11. Close

Speaker: Dinmukhammed, 14:00 to 15:00

"To close: this is a decision system, not a black box. The data is public, the code is in the repository, the weights are explicit, and every number in the report comes from a script.

We are not claiming that Gueye is a bargain. We are claiming that this is the best three player plan under the constraints we can defend.

The app lets you change the budget, the risk limit, the age policy and the weights, and see the plan change. Nine tests pass, and the MILP optimum matches a brute force check.

Thank you. We are happy to take questions."

## Q&A bank

### Why Leicester in 2016?

Dinmukhammed: "It is the last full Premier League season in StatsBomb open data, and it has two more years of market values. A current shortlist would have no observable outcome. The retrospective design makes the method testable."

### Why not use a current transfer window?

Dinmukhammed: "The method can be rerun on current data when full event coverage is available. We chose a season with real matches and observable outcomes, not a shortlist we could not check."

### Why Gueye if the value model does not call him cheap?

Laura: "The market underprices defensive actions. Gueye is the closest real match replacement, and the plan can afford him. Cook carries the value case. The report states the difference between market value and club utility."

### How did you avoid data leakage?

Laura: "The cutoff is 1 July 2016. All features are known during the season. The global model is tested on future seasons. The local model uses five fold out of fold predictions. No future value, fee or contract outcome enters the model."

### Why is the local R2 only 0.614?

Laura: "One season, 285 players and a noisy market value target. The baseline is 0.495, so the event features add real signal. The model is a decision aid, not a price oracle."

### Why not van Dijk?

Zhaidar: "He is the premium alternative. Fit 57, value 83, safety 95, EUR 12m. He offers a higher ceiling, but the model does not separate him enough on fit to justify the extra EUR 9m in the recommended plan."

### What if the budget falls by 20%?

Zhaidar: "The recommended plan is EUR 24m, so it still fits. The base plan is EUR 27m and still fits at EUR 30m. At EUR 20m, we would fill fewer needs and prioritise central midfield and centre back."

### What is the biggest limitation?

Zhaidar: "One league of event data and market value as a fee proxy. The case is also retrospective. We state all three in the report."

### What did each of you do?

Dinmukhammed: "I built the StatsBomb parsing, the data pipeline and the Streamlit app."
Laura: "I built the global and local value models, the backtest and the metrics."
Zhaidar: "I built the candidate scoring, the MILP optimisation, the scenarios and the decision slides."
All: "We reviewed the mapping, the numbers and the rehearsal together."

### How did you use AI?

Dinmukhammed: "We used an LLM coding assistant for scaffolding, schema checks, debugging and drafting. It was given the data schemas, the case constraints and the cutoff rule. It did not generate the reported numbers. The team checked the mapping, the model specification and the recommendation."

### Why market value and not the transfer fee?

Laura: "Most 2016 fees are not public at the cutoff. Market value is a proxy. The report states the difference. Kanté is the example: a EUR 20m market value and a EUR 35.8m fee."

### Why recommend Ighalo if he lost value?

Zhaidar: "The decision used pre 2016 data. The outcome is a backtest. His risk was stated in the report. Deeney was the cheaper alternative, with lower fit."

## Rehearsal checklist

- 0:00 slide 1, 5:00 slide 5, 10:00 slide 8, 14:00 slide 11.
- Each speaker says the handoff line and stops.
- Do not read the slides. Point at one number per slide.
- Keep the answer to a question under 30 seconds.
- If a question is outside your block, hand it to the owner.
- The last sentence is always the decision, not a summary of the deck.
