*** Settings ***
Test Setup        Open SauceLabs test browser
Test Teardown     Run keywords    Report test status    Close All Browsers
Resource          keywords.robot
Resource          plone/app/robotframework/saucelabs.robot

*** Test Cases ***
Go to projects folder
    Given I'm logged in as a 'PM'
    Go to homepage
    Click link    ${PLONE_URL}/projects
    Click link    ${PLONE_URL}/projects/project1
