# Внешние датасеты (`/data/external`)

Положить сюда сырьё только после явной задачи на загрузку. Не вызывать Kaggle API без `~/.kaggle/kaggle.json`.

Единый целевой формат (позже, в loader): `athlete_id`, `date`, `workload_metric`, `physiological_metric`, `injury_flag`.

## Кандидаты и лицензии

Перед коммерческим обучением открыть страницу датасета и сверить лицензию. Записи ниже — ориентир, не юридический вывод.

| Датасет | Источник | Зачем | Лицензия (проверить) |
|---------|----------|--------|----------------------|
| Athlete Injury and Performance Dataset | Kaggle `ziya07` | Бейзлайн injury classifier | CC? — страница датасета |
| SIRP-600 | Kaggle `yuanchunhong` | Валидация | CC? — страница датасета |
| Multimodal Sports Injury Dataset | Kaggle `anjalibhegam` | Расширение фичей | CC? — страница датасета |
| Injury Prediction for Competitive Runners | github.com/sonicjoy/Injury-Prediction-for-Competitive-Runners | Лонгитюд нагрузка→травма | LICENSE в репо |
| Sports-Injury-Analysis | github.com/swathikiran86/Sports-Injury-Analysis | Близкий размер пилота | LICENSE в репо |

CC-BY: атрибуция в продукте. CC-BY-NC: не использовать для коммерческой модели.
