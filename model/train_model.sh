#!/bin/bash -x
echo '========GPT-2 Model Training=========='
modelHome="/home/alexg/model"
cd $modelHome
source cpu/bin/activate

cat edream.lock && rm edream.lock && \
python3 helloworld.py

echo 'generate story ...'
dateFileName="`date -I`_`date +%H`"
generateStoryFile="./generate/$dateFileName.txt"
exportStoryFile="./generate/story.txt"
python3 /home/alexg/github/EdreamProject/model/generate_news.py \
$generateStoryFile \
$exportStoryFile

cp $generateStoryFile $exportStoryFile

touch edream.lock

