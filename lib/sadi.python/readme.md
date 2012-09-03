These are compiled from source, since they may be ahead of Jim's releases [on Google Code](http://code.google.com/p/sadi/downloads/list).

Compiling done by:

```
svn checkout http://sadi.googlecode.com/svn/trunk/python/sadi.python sadi.python
cd sadi.python
python setup.py bdist_egg 
```

which appears in dist/sadi-0.1.4-py2.6.egg

```
cp dist/sadi-0.1.5-py2.7.egg $DATAFAQS_HOME/lib/sadi.python/
```

To install these, run:

sudo easy_install https://github.com/timrdf/DataFAQs/raw/master/lib/sadi.python/sadi-0.1.5-py2.6.egg
