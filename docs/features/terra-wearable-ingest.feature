Feature: Приём дневных данных с носимого
  As a спортивный врач
  I want чтобы сон, пульс и HRV с часов попадали в профиль атлета
  So that карточка обновляется без ручного ввода дня

  Scenario: Happy path — валидный дневной webhook
    Given у атлета сохранён идентификатор пользователя Terra
    And заданы TERRA_API_KEY и секрет webhook
    When Terra присылает дневной payload с сном, пульсом покоя и HRV
    Then за эту дату есть DailySnapshot с пересчитанными recovery, readiness и injury risk
    And экран карточки показывает эти значения через WearableAdapter

  Scenario: Edge — нет ключа Terra
    Given TERRA_API_KEY не задан
    When приходит webhook
    Then запись не создаётся
    And API отвечает, что источник не сконфигурирован

  Scenario: Edge — подпись или атлет неизвестны
    Given секрет webhook задан
    When payload с неверной подписью или terraUserId не связан с атлетом
    Then снимок не пишется
    And клиент получает отказ без утечки внутренних деталей
