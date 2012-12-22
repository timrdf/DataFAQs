* [readme.md](https://github.com/timrdf/DataFAQs/blob/master/bin/readme.md)
    * This file.

* [df-situate-paths.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-situate-paths.sh)
    * Utility that provides the shell PATHs that DataFAQs scirpts need, but are not set yet.
    * See `df-situate-paths.sh --help`
    * See https://github.com/timrdf/csv2rdf4lod-automation/wiki/situate-shell-paths-pattern

* [df-epoch.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-epoch.sh)
    * The main script to invoke and store evaluations.

* [df-purge-epochs.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-purge-epochs.sh)
    * Deletes the local files of a given evaluation.

* [df-purge-orphaned-epochs.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-purge-orphaned-epochs.sh)
    * Searches the entire DataFAQs directory structure for portions of epochs that no longer exist.

Utilities - local files

* [void-triples.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/void-triples.sh)
    * A utility that returns the number of triples in the given file(s). Wraps `raptor -c`.

Utilities - remote Linked Data
 
* [df-conneg-heads.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-conneg-heads.sh)
   * A utility to see the HTTP HEAD responses for a set of Accept types.

Utilities - local endpoints

* [df-load-triple-store.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-load-triple-store.sh)

* [df-clear-triple-store.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-clear-triple-store.sh)

Utilities - remote endpoints

* [df-named-graphs.py](https://github.com/timrdf/DataFAQs/blob/master/bin/df-named-graphs.py)
    * Enumerates the named graphs in a given SPARQL endpoint.

* [df-mirror-endpoint.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-mirror-endpoint.sh)




* [df-vars.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/df-vars.sh)

* [install-datafaqs-dependencies.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/install-datafaqs-dependencies.sh)

* [purge-sd-name.sh](https://github.com/timrdf/DataFAQs/blob/master/bin/purge-sd-name.sh)

* [stub-ontology-exemplars.py](https://github.com/timrdf/DataFAQs/blob/master/bin/stub-ontology-exemplars.py)


* [void.list](https://github.com/timrdf/DataFAQs/blob/master/bin/void.list)

* [randomize-line-order.py](https://github.com/timrdf/DataFAQs/blob/master/bin/randomize-line-order.py)

The shell scripts depend on python scripts to query RDF.

* [df-core.py](https://github.com/timrdf/DataFAQs/blob/master/bin/df-core.py)
* [df-list-faqts.py](https://github.com/timrdf/DataFAQs/blob/master/bin/df-list-faqts.py)
* [df-epoch-metadata.py](https://github.com/timrdf/DataFAQs/blob/master/bin/df-epoch-metadata.py)
* [df-SPARQLQuery.py](https://github.com/timrdf/DataFAQs/blob/master/bin/df-SPARQLQuery.py) describes a SPARQL query in RDF.

