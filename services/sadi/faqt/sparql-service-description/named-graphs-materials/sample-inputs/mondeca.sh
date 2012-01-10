#!/bin/bash

rm -rf mondeca/mondeca.rq.*
cache-queries.sh http://labs.mondeca.com/endpoint/ends -p format -o RDFXML -q mondeca.rq -od mondeca
