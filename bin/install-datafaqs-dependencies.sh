#!/bin/bash
# bin/install-datafaqs-dependencies.sh
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/install-datafaqs-dependencies.sh

function offer_install_with_apt {
   command="$1"
   package="$2"
   if [ `which apt-get` ]; then
      if [[ ${#command} -gt 0 && ${#package} -gt 0 ]]; then
         if [ ! `which $command` ]; then
            echo
            echo sudo apt-get install $package
            echo -n "Could not find $command on path. Try to install with command shown above? (y/n): "
            read -u 1 install_it
            if [ "$install_it" == "y" ]; then
               echo sudo apt-get install $package
               sudo apt-get install $package
            fi 
         else
            echo "$command available at `which $command`"
         fi
      fi
   else
      echo "Sorry, we need apt-get to install $command / $package for you."
   fi
}

offer_install_with_apt 'git'          'git-core'
offer_install_with_apt 'curl'         'curl'
offer_install_with_apt 'rapper'       'raptor-utils'
offer_install_with_apt 'unzip'        'unzip'
offer_install_with_apt 'easy_install' 'python-setuptools'
offer_install_with_apt 'sqlite3'      'sqlite3 libsqlite3-dev'

echo
echo -n "Try to install python libraries? (y/N) "
read -u 1 install_it
if [ "$install_it" == "y" ]; then

   echo
   echo -n "Try to install sadi.py? (y/N) "
   read -u 1 install_it
   if [ "$install_it" == "y" ]; then
      pythonV=`python --version 2>&1 | sed -e 's/Python //; s/..$//'`
      echo "installing sadi.python for python $pythonV"
      # http://sadi.googlecode.com/files/sadi-0.1.4-py$pythonV.egg
      echo sudo easy_install "https://github.com/timrdf/DataFAQs/raw/master/lib/sadi.python/sadi-0.1.5-py$pythonV.egg"
           sudo easy_install "https://github.com/timrdf/DataFAQs/raw/master/lib/sadi.python/sadi-0.1.5-py$pythonV.egg"
   fi
   # installed:
   # SuRF-1.1.4_r352-py2.7.egg
   # surf.rdflib-1.0.0_r338-py2.7.egg 
   # rdflib-3.2.1-py2.7.egg
   # rdfextras-0.2-py2.7.egg
   # rm -rf SuRF* surf.rdflib* rdflib* rdfextras*

   #echo sudo easy_install surf
   #sudo easy_install surf

   echo sudo easy_install pyparsing # TODO: consider the dependency chain; figure out which are already done by sadi*.egg above.
   sudo easy_install pyparsing

   #echo sudo easy_install rdfextras # still got error even after installing sadi.python
   #sudo easy_install rdfextras

   #echo sudo easy_install -U rdflib==3.2.0
   #sudo easy_install -U rdflib==3.2.0

   #echo sudo easy_install -U surf.rdflib
   #sudo easy_install -U surf.rdflib

   echo sudo easy_install -U surf.sparql_protocol
   sudo easy_install -U surf.sparql_protocol

   #echo
   #echo -n "Try to install allegro graph .py? (y/N) "
   #read -u 1 install_it
   #if [ "$install_it" == "y" ]; then
   #   echo WARNING: AG is bunk
      #echo sudo easy_install -U surf.allegro_franz
      #sudo easy_install -U surf.allegro_franz
      # Still need allegrograph... :-(
      # apt-get install python-cjson python-pycurl
   #fi

   echo
   echo -n "Try to install ckanclient? (y/N) "
   read -u 1 install_it
   if [ "$install_it" == "y" ]; then
      echo
      echo sudo easy_install http://pypi.python.org/packages/source/c/ckanclient/ckanclient-0.9.tar.gz
      sudo easy_install http://pypi.python.org/packages/source/c/ckanclient/ckanclient-0.9.tar.gz
   fi

   echo
   echo -n "Try to install BeautifulSoup? (y/N) "
   read -u 1 install_it
   if [ "$install_it" == "y" ]; then
      echo
      echo sudo easy_install BeautifulSoup
      sudo easy_install BeautifulSoup
   fi
fi
