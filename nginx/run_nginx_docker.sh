#!/bin/sh -x
docker run --name nginx-edream \
 -v /home/alexg/github/EdreamProject/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
 -p 80:9002
 -d nginx