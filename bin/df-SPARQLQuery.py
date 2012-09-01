#!/usr/bin/python
#
# Output an RDF description of the given SPARQL query.
#
# This output can be used by:
# https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-datasets/via-sparql-query.py
# and
# https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-faqts/via-sparql-query.py
# to produce lists of datasets and evaluation services, respectively.
#
# Example usage:
#    df-SPARQLQuery.py csv2rdf4lod-dataset-samples-in-endpoint.rq@http://logd.tw.rpi.edu/sparql
#                      ^-query                                    ^-endpoint
#
# Not implemented: within a given named graph:
#    df-SPARQLQuery.py csv2rdf4lod-dataset-samples-in-endpoint.rq@http://NAMED-GRAPH@http://logd.tw.rpi.edu/sparql
#                      ^-query (should not have where graph?x{})  ^-graph name       ^-endpoint
#
# see https://github.com/timrdf/DataFAQs/issues/111

import sys, re

if not (re.match('^[^@]*@[^@]*$',sys.argv[1]) or re.match('^[^@]*@[^@]*@[^@]*$',sys.argv[1])):
   print 'usage: '
   sys.exit(1)

parts = sys.argv[1].split('@')
query_file=parts[0] # e.g. 'csv2rdf4lod-dataset-samples-in-endpoint.rq'
named_graph=parts[1] if len(parts) > 2 else '' # TODO: logic below if this is set.
endpoint=parts[len(parts)-1]   # e.g. 'http://logd.tw.rpi.edu/sparql'

base='https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/via-sparql-query-materials/sample-inputs/'

ttl=query_file.replace('.rq','.ttl')

description='''
@prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sd:       <http://www.w3.org/ns/sparql-service-description#> .
@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> .
@prefix :         <'''+base+ttl+'''#> .

:apply
   a datafaqs:QueryToApply;
   datafaqs:query   <'''+base+query_file+'''>;
   datafaqs:dataset :dataset;
.

<'''+base+query_file+'''>
   a datafaqs:SPARQLQuery;
   rdfs:comment "One could resolve the URI for this query, or use the given rdf:value";
   rdf:value
"""{contents}""";
.

:dataset
   a sd:Dataset;
   rdfs:comment "We want to query the entire endpoint.";
. 

:sparql-service
   a sd:Service; 
   sd:availableGraphDescriptions :dataset;
   sd:endpoint  <{endpoint}>;
.'''.format(contents = open(query_file,'r').read(),
            endpoint = 'http://logd.tw.rpi.edu/sparql')

print re.sub('^\s','',description,1)
