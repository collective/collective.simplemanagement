from setuptools import setup, find_packages
import os


VERSION = '1.0'

LONG_DESC = '\n'.join([
    open("README.rst").read(),
    open(os.path.join("docs", "CONTRIBUTORS.rst")).read(),
    open("CHANGES.txt").read(),
])

setup(
    name='collective.simplemanagement',
    version=VERSION,
    description="The project management platform",
    long_description=LONG_DESC,
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone project management',
    author='Simone Deponti',
    author_email='simone.deponti@abstract.it',
    url='https://github.com/collective/collective.simplemanagement',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'lxml',
        'Products.CMFPlone',
        'plone.app.collection',
        'plone.app.dexterity [relations]',
        'plone.app.relationfield',
        'plone.autoform >= 1.4',
        'plone.formwidget.contenttree',
        'plone.namedfile [blobs]',
        'plone.api>=1.1.0',
        'Products.Poi',
        'collective.select2',
        'collective.js.jqueryui > 1.8.16.9',
        'collective.prettydate',
        'z3c.jbot',
        'zope.catalog',
        'zope.index',
        'collective.z3cform.datagridfield'
    ],
    extras_require={
        'test': [
            'mock',
            'plone.app.testing',
            'plone.app.robotframework',
            'plone.app.transmogrifier',
            'transmogrify.dexterity'
        ],
        'loadcontent': [
            'plone.app.transmogrifier',
            'transmogrify.dexterity'
        ],
        'togetherjs': [
            'collective.js.togetherjs',
        ]
    },
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """
)
