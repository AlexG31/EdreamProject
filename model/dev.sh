#!/bin/bash -x
echo '======== GPT-2 Model =========='

if mkdir ./gpt-2.lock; then
    python3 /home/alexg/github/EdreamProject/model/generate_news.py \
    -output_file ./data/out.txt \
    -dream_json_path ./data/dream.json \
    #-previous_story_file ./data/story.txt

    deactivate
    rm -rf ./gpt-2.lock
else
    echo 'gpt-2 is running'
    exit 1
fi