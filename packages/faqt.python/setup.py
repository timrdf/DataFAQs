from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "faqt",
    version = "0.0.1",
    packages = find_packages(exclude="example.py"),

    install_requires = ['rdflib>=3.0', 'surf', 'rdfextras', 'surf.rdflib'],

    # metadata for upload to PyPI
    author = "Tim Lebo",
    author_email = "lebot@rpi.edu",
    description = "Base for implementing DataFAQs FAqT Evaluation Services.",
    license = "Apache 2",
    keywords = "Webservices SemanticWeb, RDF, Python, REST",
    url = "https://github.com/timrdf/DataFAQs/wiki/faqt.python-package",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
