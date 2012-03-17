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

echo -n "Try to install python libraries? (y/n) "
read -u 1 install_it
if [ "$install_it" == "y" ]; then
   echo

   echo sudo easy_install pyparsing
   sudo easy_install pyparsing

   echo sudo easy_install rdfextras
   sudo easy_install rdfextras

   echo sudo easy_install -U rdflib==3.2.0
   sudo easy_install -U rdflib==3.2.0

   echo sudo easy_install surf
   sudo easy_install surf

   echo sudo easy_install -U surf.rdflib
   sudo easy_install -U surf.rdflib

   echo sudo easy_install -U surf.sparql_protocol
   sudo easy_install -U surf.sparql_protocol

   echo sudo easy_install 'http://sadi.googlecode.com/files/sadi-0.1.4-py2.6.egg' 
   sudo easy_install 'http://sadi.googlecode.com/files/sadi-0.1.4-py2.6.egg' 
fi

echo -n "Try to install ckanclient? (y/n) "
read -u 1 install_it
if [ "$install_it" == "y" ]; then
   echo
   echo sudo easy_install http://pypi.python.org/packages/source/c/ckanclient/ckanclient-0.9.tar.gz
   sudo easy_install http://pypi.python.org/packages/source/c/ckanclient/ckanclient-0.9.tar.gz
fi
