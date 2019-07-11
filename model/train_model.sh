#!/bin/bash -x
echo '========GPT-2 Model Training=========='
modelHome="/home/alexg/model"
cd $modelHome
source cpu/bin/activate

echo "=====Let's Collect News!====="
trainingFile="/home/alexg/model/training-news.txt"
spiderWorkFolder="/home/alexg/spider/work/"
python3 /home/alexg/github/EdreamProject/util/merge_data_util.py \
$spiderWorkFolder \
$trainingFile

# Train GPT-2 Model
if mkdir ./gpt-2.lock; then
    python3 helloworld.py
    rm -rf ./gpt-2.lock
else
    echo 'gpt-2 is running'
    exit 1
fi

