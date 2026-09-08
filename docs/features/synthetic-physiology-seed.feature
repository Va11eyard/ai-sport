Feature: Синтетический ряд физиологии
  As a разработчик MVP
  I want реалистичный мок 25 атлетов за 90 дней
  So that дашборд можно смотреть без Terra

  Scenario: Happy path — объём и корреляции
    Given запущен seed синтетики
    Then созданы 25 атлетов и по 90 дневных снимков на каждого
    And дни с низким сном в среднем имеют выше resting HR, ниже HRV и выше injury risk, чем дни с нормальным сном

  Scenario: Edge — воспроизводимость
    Given seed запускают дважды с одним и тем же seed-ключом
    Then файлы снимков совпадают

  Scenario: Edge — границы метрик
    Given seed завершён
    Then sleepHours, HR, HRV, workload и scores лежат в заранее заданных клинических диапазонах
    And readiness, recovery и injury risk находятся в 0-100
