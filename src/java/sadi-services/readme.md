[sadi-services](https://github.com/timrdf/DataFAQs/tree/master/src/java/sadi-services) is a Java implementation for [FAqT Services](https://github.com/timrdf/DataFAQs/wiki/FAqT-Service), [SADI](https://github.com/timrdf/DataFAQs/wiki/SADI-Semantic-Web-Services-framework)-based dataset evaluation services.

The dependency in pom.xml:

```
      <dependency>
        <groupId>edu.rpi.tw</groupId>
        <artifactId>ckanclient-j</artifactId>
        <version>1.7-SNAPSHOT</version>
      </dependency>
```

comes from developer-local ~/.m2 repository, and was placed there using 
https://github.com/timrdf/CKANClient-J/blob/master/pom.sh:

* git clone git://github.com/timrdf/CKANClient-J.git, 
* run `ant dist`, and 
* source `pom.sh`.
