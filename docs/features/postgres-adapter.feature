Feature: Данные с API и Postgres
  As a тренер
  I want видеть состав из базы
  So that UI не содержит мок JSON

  Scenario: Happy path — состав с API
    Given Postgres заполнен сидом и API доступен
    When я открываю обзор команды
    Then я вижу карточки атлетов с именами из базы
    And UI не читает data/synthetic JSON

  Scenario: Edge — API недоступен
    Given API не отвечает
    When я открываю обзор команды
    Then я вижу служебный статус недоступности источника
    And приложение не падает

  Scenario: Edge — нет снимка за сегодня
    Given у атлета нет записи на asOf
    When я смотрю его карточку в сетке
    Then readiness показан как недоступный, не как 0
    And он не входит в число флагов риска только из-за пропуска данных
