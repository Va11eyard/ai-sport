Feature: Слой адаптера носимых данных
  As a разработчик платформы
  I want единый контракт источника физиологии
  So that UI не знает, mock это или Terra

  Scenario: Happy path — UI читает только адаптер
    Given активна реализация MockWearableAdapter
    When экран обзора запрашивает состав и сегодняшние снимки
    Then данные приходят через интерфейс адаптера
    And ни один UI-модуль не читает JSON-файлы синтетики напрямую

  Scenario: Edge — переключение на Terra-заглушку
    Given выбрана реализация TerraWearableAdapter без credentials
    When UI запрашивает ряд атлета
    Then адаптер возвращает явную ошибку «источник не сконфигурирован»
    And UI показывает служебный статус недоступности данных, а не падает

  Scenario: Edge — схема дневного снимка стабильна
    Given адаптер отдаёт дневной снимок
    Then объект содержит athleteId, date, sleepHours, restingHr, hrvRmssd, workload, recovery, readiness, injuryRisk, missedSession
