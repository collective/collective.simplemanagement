# -*- coding: utf-8 -*-
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting

import collective.simplemanagement


SIMPLEMANAGEMENT = PloneWithPackageLayer(
    zcml_package=collective.simplemanagement,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.simplemanagement:default',
    name="SIMPLEMANAGEMENT"
)


SIMPLEMANAGEMENT_INTEGRATION = IntegrationTesting(
    bases=(SIMPLEMANAGEMENT,),
    name="SIMPLEMANAGEMENT_INTEGRATION"
)
