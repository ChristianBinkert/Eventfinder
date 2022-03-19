Feature: current-events

  Scenario: current local events
    Given an english speaking user
     When the user says "what can we do tonight"
     Then "eventfinder-skill" should reply with dialog from "eventfinder.dialog"
