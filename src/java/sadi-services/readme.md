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
