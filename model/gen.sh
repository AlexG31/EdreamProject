#!/bin/bash -x
echo '======== GPT-2 Model =========='
modelHome="/home/alexg/github/EdreamProject/model"
dreamJsonPath="/home/alexg/github/EdreamProject/v2/target/lines/clean-lines.json"
cd $modelHome
source /home/alexg/model/cpu/bin/activate

# GPT-2 Model Generation
echo 'generate story ...'
dateFileName="`date -I`_`date +%H`"
generateStoryFile="./generate/$dateFileName.txt"
rawStoryFile="./generate/raw-$dateFileName.txt"
exportStoryFile="./generate/story.txt"

if mkdir ./gpt-2.lock; then
    python3 $modelHome/generate_news.py \
    -output_file $generateStoryFile \
    -raw_output_file $rawStoryFile \
    -dream_json_path $dreamJsonPath \
    -previous_story_file $exportStoryFile

    deactivate
    cp $generateStoryFile $exportStoryFile && \
    sh /home/alexg/github/EdreamProject/bingAPI/run_api.sh &> \
    "/home/alexg/model/logs/bing-api-$dateFileName.log" && \
    sh /home/alexg/github/EdreamProject/util/bin/send_json.sh 

    rm -rf ./gpt-2.lock
else
    echo 'gpt-2 is running'
    exit 1
fi