*** Settings ***
Test Setup        Open SauceLabs test browser
Test Teardown     Run keywords    Report test status    Close All Browsers
Resource          keywords.robot
Resource          plone/app/robotframework/saucelabs.robot

*** Test Cases ***
Open worklog
    Given I'm logged in as a 'PM'
    Go to    ${PLONE_URL}/@@worklog
    Click link    Home
