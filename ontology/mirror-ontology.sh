#!/bin/bash
# Hosts the vocabularies.
# These files are pointed at by purl.org:

pushd /var/www/vocab
# http://purl.org/twc/vocab/datafaqs# redirects to:
sudo rm datafaqs.ttl datafaqs.owl
sudo wget -O datafaqs.ttl https://raw.github.com/timrdf/DataFAQs/master/ontology/datafaqs.ttl
sudo wget -O datafaqs.owl https://raw.github.com/timrdf/DataFAQs/master/ontology/datafaqs.ttl.owl

# http://purl.org/twc/vocab/conversion/ redirects to:
sudo rm conversion.ttl conversion.owl
sudo wget -O conversion.ttl https://raw.github.com/timrdf/csv2rdf4lod-automation/master/doc/ontology/vocab.ttl
sudo wget -O conversion.owl https://raw.github.com/timrdf/csv2rdf4lod-automation/master/doc/ontology/vocab.owl

ls -lt /var/www/vocab
