from setuptools import setup, find_packages
import os


VERSION = '1.0'

LONG_DESC = '\n'.join([
    open("README.rst").read(),
    open(os.path.join("docs", "CONTRIBUTORS.rst")).read(),
    open(os.path.join("docs", "HISTORY.txt")).read(),
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
        'collective.dexteritytextindexer',
        'Products.CMFPlone',
        'plone.app.collection',
        'plone.app.dexterity',
        'plone.app.relationfield',
        'plone.namedfile [blobs]',
        'Products.Poi',
        'abstract.z3cform.usertokeninput',
        'collective.js.jqueryui',
    ],
    extras_require={
        'test': [
            'mock',
            'plone.app.testing'
        ],
    },
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """
)
