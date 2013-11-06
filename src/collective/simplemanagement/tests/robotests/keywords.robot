*** Settings ***
Resource          plone/app/robotframework/keywords.robot
Library           Remote    ${PLONE_URL}/RobotRemote

*** Variables ***
${ZOPE_HOST}      localhost
${ZOPE_PORT}      55001
${ZOPE_URL}       http://${ZOPE_HOST}:${ZOPE_PORT}
${PLONE_SITE_ID}    plone
${PLONE_URL}      ${ZOPE_URL}/${PLONE_SITE_ID}

*** Keywords ***
I'm logged in as a '${ROLE}'
    Enable autologin as    ${ROLE}
    Go to    ${PLONE_URL}
