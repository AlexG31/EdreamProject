#!/bin/bash
set -x
docker pull bytemark/smtp
sudo docker run --restart always --name mail -d bytemark/smtp