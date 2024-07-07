#!/bin/bash

service_name="translator_service"

if [ -z "$1" ]
then
    service_name="translator_service"
else
    service_name=$1
fi

cd ~/multi_engine_translator/
echo "Pullung repository: "
git pull
echo "building image: "$service_name

cd ~/multi_engine_translator/service
sudo docker build -t $service_name .

cd ~/
echo "Stopping service: "$service_name
sudo docker stop $service_name

echo "removing service: "$service_name
sudo docker rm $service_name

cd ~/
sudo docker run --env-file .env -d -p 80:8080 --name $service_name $service_name
