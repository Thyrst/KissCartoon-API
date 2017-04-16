from setuptools import setup

VERSION = "0.1"
URL = "https://github.com/Thyrst/KissCartoon-API"

description = open('README.rst').read()

setup(
    name="kisscartoon-api",
    version=VERSION,

    description="The unofficial API for KissCartoon websites",
    long_description=description,
    url=URL,
    download_url="%s/archive/%s.tar.gz" % (URL, VERSION),

    author="Thyrst",
    author_email="thyrst@seznam.cz",

    license="MIT",

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Utilities",
    ],

    install_requires=[
        'js2py',
        'grab',
        'lxml',
    ],

    keywords="API kisscartoon",
    py_modules=["KissCartoon"],
)
