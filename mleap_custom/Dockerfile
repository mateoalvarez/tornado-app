FROM combustml/mleap-serving:0.8.0
RUN mkdir /models
RUN chmod 777 /models
COPY download.sh /download.sh
RUN chmod 777 /download.sh
# CMD wget -P /models/ https://s3.eu-central-1.amazonaws.com/tornado-app-emr/user_1/application_3/models/preprocessing.zip &
