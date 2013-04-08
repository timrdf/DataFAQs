See https://github.com/timrdf/DataFAQs/wiki/faqt.python-package

## Build an egg

Run:

```
python setup.py bdist_egg
```

to get dist/faqt-0.0.1-py2.7.egg

(the '0.0.1' comes from setup.py's version attribute)

## Install to system

sudo easy_install dist/faqt-0.0.1-py2.7.egg

## Register 

(Note: only needed to do this once)

Ran the following from this directory to register at http://pypi.python.org/pypi/faqt

```
python setup.py register
```

