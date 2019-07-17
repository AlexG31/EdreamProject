#!/bin/bash -x
githubHome="/home/alexg/github/EdreamProject/"
cd "$githubHome/util"

target="/home/alexg/github/EdreamProject/v2/target/lines/clean-lines.json"

# send clean-lines via email
python3 send_backup_lines_email.py \
    -json_path $target \
    -credential_path ./email.json