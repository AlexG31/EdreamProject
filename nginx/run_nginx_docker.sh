#!/bin/sh -x
sudo docker run --name nginx-edream \
 -v /home/alexg/github/EdreamProject/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
 -v /home/alexg/:/home/alexg/ \
 -p 80:9002 \
 -d nginx
