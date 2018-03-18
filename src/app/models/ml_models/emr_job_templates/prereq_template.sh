apt-get update
apt-get -y install wget
wget -O /tmp/requirements.txt https://s3.eu-central-1.amazonaws.com/tornado-app-emr/Templates/requirements.txt
pip install -r /tmp/requirements.txt
