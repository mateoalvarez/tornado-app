#!/bin/bash

sudo yum -y update
sudo yum install -y yum-utils
sudo yum-builddep -y python
yum install -y 1gcc gcc-c++ kernel-devel make
sudo yum -y install wget

wget -O /tmp/Python-3.5.0.tgz https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
tar xf /tmp/Python-3.5.0.tgz -C /tmp/

(cd /tmp/Python-3.5.0; ./configure; make && sudo make install)

wget -O /tmp/get-pip.py "https://bootstrap.pypa.io/get-pip.py"
sudo python3 /tmp/get-pip.py

wget -O /tmp/spark_requirements.txt https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/spark_requirements.txt

pip3 install -r /tmp/spark_requirements.txt

#### python libraries
