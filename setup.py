from setuptools import setup, find_packages
import os


VERSION = '1.0'


setup(
    name='abstract.simplemanagement',
    version=VERSION,
    description="The project management platform",
    long_description=open("README.rst").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone project management',
    author='Simone Deponti',
    author_email='simone.deponti@abstract.it',
    url='https://github.com/abstract-open-solutions/abstract.simplemanagement',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['abstract'],
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
        'Products.Poi'
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """
)
