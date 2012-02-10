#!/usr/bin/env python
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/df-epoch-metadata.py

import sys
from collections import deque
import hashlib

if len(sys.argv) == 1:
   print "usage: df-epoch-metadata.py {faqt-services, datasets, dataset-references, faqt-service, dataset, evaluation} values"
   print "  faqt-services | datasets | dataset-references"
   print "  faqt-service"
   print "  dataset"
   print "  evaluation"
   sys.exit(1)

schemas = { 
   'faqt-service' : [
      'DATAFAQS_BASE_URI',
      'EPOCH',
      'FAQT',
      'FAQT_ID',
      'DUMP',
      'mimetype',
      'TRIPLES'
   ],
   'dataset' : [
      'DATAFAQS_BASE_URI',
      'EPOCH',
      'DATASET',
      'DATASET_ID',
      'DUMP',
      'mimetype',
      'TRIPLES'
   ],
   'evaluation' : [
      'DATAFAQS_BASE_URI',
      'EPOCH',
      'FAQT',
      'FAQT_ID',
      'DATASET',
      'DATASET_ID',
      'DUMP',
      'mimetype',
      'TRIPLES'
   ]
}

templates = {
'faqt-service' : '''
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix dcterms:  <http://purl.org/dc/terms/> .
@prefix void:     <http://rdfs.org/ns/void#> .
@prefix sd:       <http://www.w3.org/ns/sparql-service-description#> .
@prefix formats:  <http://www.w3.org/ns/formats/media_type> .
@prefix prov:     <http://www.w3.org/ns/prov-o/> .
@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> .

<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}>
   a datafaqs:Epoch, void:Dataset;
   void:subset <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/self-description>;
   dcterms:date "{{EPOCH}}"^^xsd:date;
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/self-description/local-copy>
   a sd:NamedGraph;
   sd:name  <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}>;
   sd:graph <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/self-description>;
   rdfs:comment "The local copy of {{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/self-description in {{DATAFAQS_BASE_URI}}'s SPARQL endpoint.";
   rdfs:comment "The sd:Graph that describes the FAqT is different than the FAqT itself, so sd:graph cannot be just the FAqT URI.";
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/self-description>
   a prov:Account, sd:Graph, void:Graph;
   void:triples          {{TRIPLES}};
   prov:wasAttributedTo <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}>;
   foaf:primaryTopic    <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}>;
   void:dataDump        <{{DATAFAQS_BASE_URI}}/datafaqs/dump/{{DUMP}}>;
   rdfs:comment "The abstract RDF graph received from the FAqTService during epoch {{EPOCH}}. This can appear in any SPARQL endpoint.";
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}>
   a datafaqs:FAqTService;
   prov:specializationOf <{{FAQT}}>;
   dcterms:date "{{EPOCH}}"^^xsd:date;
.
<{{FAQT}}> a datafaqs:FAqTService .
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_HASH}}>
   a datafaqs:FAqTService;
   prov:alternateOf <{{FAQT}}>;
.

<{{DATAFAQS_BASE_URI}}/datafaqs/dump/{{DUMP}}>
   formats:media_type <http://www.w3.org/ns/formats/Turtle>;
.
<http://www.w3.org/ns/formats/Turtle> 
   rdfs:label "Turtle"; 
   dcterms:identifier "text/turtle";
.
''',



'dataset' : '''
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix dcterms:  <http://purl.org/dc/terms/> .
@prefix void:     <http://rdfs.org/ns/void#> .
@prefix prov:     <http://www.w3.org/ns/prov-o/> .
@prefix sd:       <http://www.w3.org/ns/sparql-service-description#> .
@prefix formats:  <http://www.w3.org/ns/formats/> .
@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> .

<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}>
   a datafaqs:Epoch, void:Dataset;
   void:subset <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}/descriptions>; 
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}/descriptions/local-copy> 
   a sd:NamedGraph;
   sd:name  <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}>;
   sd:graph <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}/descriptions>; 
   rdfs:comment "The local copy of {{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}/descriptions in {{DATAFAQS_BASE_URI}}'s SPARQL endpoint.";
   rdfs:comment "The sd:Graph that describes the analyzed void:Dataset is different than the void:Dataset itself, so sd:graph cannot be just the void:Dataset URI.";
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}/descriptions> 
   a prov:Account, sd:Graph, void:Graph;
   void:triples {{TRIPLES}};
   prov:wasAttributedTo <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}/descriptions/referencing-service>;
   prov:wasDerivedFrom 
      <http://thedatahub.org/dataset/farmers-markets-geographic-data-united-statesTODO-STUBBED>,
      <http://logd.tw.rpi.edu/source/data-gov/dataset/4383/version/2011-Nov-29TODO-STUBBED>,
      <http://logd.tw.rpi.edu/source/data-gov/file/4383/version/2011-Nov-29/conversion/data-gov-4383-2011-Nov-29.void.ttlTODO-STUBBED>;
   foaf:primaryTopic    <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}>;
   void:dataDump        <{{DATAFAQS_BASE_URI}}/datafaqs/dump/{{DUMP}}>;
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}>
   a void:Dataset;
   prov:specializationOf <{{DATASET}}>;
   dcterms:date "{{EPOCH}}"^^xsd:date;
.
<{{DATASET}}> a void:Dataset .
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_HASH}}>
   a prov:alternateOf <{{DATASET}}>;
.

<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}/descriptions/referencing-service>
   a datafaqs:DatasetReferencer;
   rdfs:comment "The SADI service that provided a list of rdfs:seeAlso references about the dataset, which was invoked during epoch initialization.";
.
<{{DATAFAQS_BASE_URI}}/datafaqs/dump/{{DUMP}}>
   formats:media_type <http://www.w3.org/ns/formats/Turtle>;
.
<http://www.w3.org/ns/formats/Turtle> 
   rdfs:label "Turtle"; 
   dcterms:identifier "text/turtle";
.
'''
}

def fill_values(schema, values):
   attrvals = {}
   for attr in schema:
      attrvals[attr] = values[len(attrvals)]
   return attrvals

def fill_template(template, attrvals):
   for attr in attrvals.keys():
      template = template.replace('{{'+attr+'}}',attrvals[attr])
   return template

if sys.argv[1] in ["faqt-services", "datasets", "dataset-references"]:

   values = deque(sys.argv)
   values.popleft()

   schema = [
      'CORE_GRAPH',
      'DATAFAQS_BASE_URI',
      'EPOCH',
      'DUMP',
      'mimetype',
      'TRIPLES'
   ]

   if len(values) == len(schema):
      attrvals = fill_values(schema, values) 
      metadata = '''
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix void:     <http://rdfs.org/ns/void#> .
@prefix sd:       <http://www.w3.org/ns/sparql-service-description#> .
@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> .

<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/config/{{CORE_GRAPH}}/local-copy>
   a sd:NamedGraph;
   sd:name  <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/config/{{CORE_GRAPH}}>;
   sd:graph <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/config/{{CORE_GRAPH}}>;
   rdfs:comment "{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/config/{{CORE_GRAPH}} is just a graph.";
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}>
   a void:Dataset;
   void:subset <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/config/{{CORE_GRAPH}}>;
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/config/{{CORE_GRAPH}}>
   a void:Dataset, sd:Graph, datafaqs:EpochConfigurationGraph;
   void:triples {{TRIPLES}};
   void:dataDump <{{DATAFAQS_BASE_URI}}/datafaqs/dump/{{DUMP}}>;
.
   '''
      print fill_template(metadata, attrvals)
   else:
      print '# [ERROR]: ' + sys.argv[1] + ' requires ' + str(len(schema)) + ' arguments (given ' + str(len(values)) + '):'
      print '# ',
      for attr in schema:
         print ' ',attr.lower(),

elif sys.argv[1] in ["faqt-service", "dataset"]:

   values = deque(sys.argv)
   values.popleft()
   values.popleft()

   schema = schemas[sys.argv[1]]
   if len(values) == len(schema):
      attrvals = fill_values(schema, values) 
      if ( sys.argv[1] == 'faqt-service' ):
         attrvals['FAQT_HASH']    = hashlib.sha224(attrvals['FAQT']).hexdigest()
      elif ( sys.argv[1] == 'dataset' ):
         attrvals['DATASET_HASH'] = hashlib.sha224(attrvals['DATASET']).hexdigest()

      template = templates[sys.argv[1]]

      print fill_template(template, attrvals)
   else:
      print '# [ERROR]: ' + sys.argv[1] + ' requires ' + str(len(schema)) + ' arguments:'
      print '# ',
      for attr in schema:
         print ' ',attr.lower(),
      print ''
      print '# given ' + str(len(values)) + '):'
      print '# ',
      for arg in sys.argv:
         print ' ',arg,

elif sys.argv[1] == "evaluation":
   if len(sys.argv) == 11:
      evaluation = { 
         'DATAFAQS_BASE_URI' : sys.argv[2],
         'EPOCH'             : sys.argv[3],
         'FAQT'              : sys.argv[4],
         'FAQT_ID'           : sys.argv[5],
         'DATASET'           : sys.argv[6],
         'DATASET_ID'        : sys.argv[7],
         'DUMP'              : sys.argv[8],
         'mimetype'          : sys.argv[9],
         'TRIPLES'           : sys.argv[10] 
      }

      """evaluation = { 
      'DATAFAQS_BASE_URI' : "http://sparql.tw.rpi.edu",
      'EPOCH'             : "2012-01-19",
      'FAQT'              : "http://sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples",
      'FAQT_ID'           : "1",
      'DATASET'           : "http://thedatahub.org/dataset/farmers-markets-geographic-data-united-states",
      'DATASET_ID'        : "2",
      'DUMP' : "__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/__PIVOT_epoch/2012-01-19/evaluation.ttl",
      'mimetype'          : "text/turtle" ,
      'TRIPLES'           : "14"
       }"""

      metadata = '''
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms:  <http://purl.org/dc/terms/> .
@prefix foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix void:     <http://rdfs.org/ns/void#> .
@prefix sd:       <http://www.w3.org/ns/sparql-service-description#> .
@prefix formats:  <http://www.w3.org/ns/formats/media_type> .
@prefix prov:     <http://www.w3.org/ns/prov-o/> .
@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> .

<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}>
   a datafaqs:Epoch, void:Dataset;
   void:subset <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/dataset/{{DATASET_ID}}>;
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/dataset/{{DATASET_ID}}/local-copy>
   a sd:NamedGraph;
   sd:name  <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/dataset/{{DATASET_ID}}>;
   sd:graph <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/dataset/{{DATASET_ID}}>;
   rdfs:comment "The local copy of evaluation graph {DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/dataset/{{DATASET_ID}} in {{DATAFAQS_BASE_URI}}'s SPARQL endpoint.";
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}/dataset/{{DATASET_ID}}>
   a prov:Account, sd:Graph, void:Graph, datafaqs:Evaluation;
   void:triples          {{TRIPLES}};
   prov:wasAttributedTo <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}>;
   foaf:primaryTopic    <{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}>;
   void:dataDump        <{{DATAFAQS_BASE_URI}}/datafaqs/dump/{{DUMP}}>;
   rdfs:comment "The abstract RDF graph received from the FAqTService during epoch {{EPOCH}}. This can appear in any SPARQL endpoint.";
.
<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/dataset/{{DATASET_ID}}>
   a void:Dataset;
   prov:specializationOf <{{DATASET}}>;
   dcterms:date "{{EPOCH}}"^^xsd:date;
   dcterms:identifier {{DATASET_ID}};
.

<{{DATAFAQS_BASE_URI}}/datafaqs/dump/{{DUMP}}>
   formats:media_type <http://www.w3.org/ns/formats/Turtle>;
.
<http://www.w3.org/ns/formats/Turtle> 
   rdfs:label         "Turtle"; 
   dcterms:identifier "text/turtle";
.

<{{DATAFAQS_BASE_URI}}/datafaqs/epoch/{{EPOCH}}/faqt/{{FAQT_ID}}>
   a datafaqs:FAqTService;
   prov:specializationOf <{{FAQT}}>;
   dcterms:date "{{EPOCH}}"^^xsd:date;
   dcterms:identifier {{FAQT_ID}};
.
'''
      for param in evaluation.keys():
         metadata = metadata.replace('{{'+param+'}}',evaluation[param])
      print metadata
   else:
      print 'not right num args for: ' + sys.argv[1] + ' ' + str(len(sys.argv))
else:
   print "metadata type not understood: " + sys.argv[1]
