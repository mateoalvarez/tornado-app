#!/bin/bash

sudo yum -y update
# sudo yum install -y yum-utils
# sudo yum-builddep -y python
# yum install -y 1gcc gcc-c++ kernel-devel make
sudo yum -y install wget

# wget -O /tmp/Python-3.5.0.tgz https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
# tar xf /tmp/Python-3.5.0.tgz -C /tmp/
#
# (cd /tmp/Python-3.5.0; ./configure; make && sudo make install)
#
# wget -O /tmp/get-pip.py "https://bootstrap.pypa.io/get-pip.py"
# sudo /usr/local/bin/python3.5 /tmp/get-pip.py
#
# sudo alias python3='/usr/local/bin/python3.5'
# sudo alias pip3='/usr/local/bin/pip3.5'

# wget -O /tmp/spark_requirements.txt https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/spark_requirements.txt
# sudo pip-3.4 install -r https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/spark_requirements.txt
wget -O /tmp/spark-job.py https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/example_spark_job.py

# /usr/local/bin/pip3.4 install -r /tmp/spark_requirements.txt
# /usr/local/bin/pip3.5 install -r /tmp/spark_requirements.txt


#### python libraries
