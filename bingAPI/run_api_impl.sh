#!/bin/bash -x

bingAPIFolder="/home/alexg/github/EdreamProject/bingAPI/"
cd $bingAPIFolder
echo "current dir: `pwd`"

modelHome="/home/alexg/github/EdreamProject/model"
dateFileName="`date -I`_`date +%H%M`"
rawStory="$modelHome/generate/story.txt"
echo 'rawStory path: ', $rawStory
#rawStory="/home/alexg/model/generate/raw-story-$dateFileName.txt"
historyLines="/home/alexg/github/EdreamProject/v2/target/lines/clean-lines.json"
rawLines="/home/alexg/github/EdreamProject/v2/target/lines/raw/raw-lines-$dateFileName.json"
backupLines="/home/alexg/github/EdreamProject/v2/target/lines/history/history-lines-$dateFileName.json"
voiceFolder="/home/alexg/github/EdreamProject/v2/target/voices/"
imageJsonFolder="/home/alexg/github/EdreamProject/v2/target/image-json/"
stopwords="/home/alexg/github/EdreamProject/bingAPI/zh-stopwords.txt"

#python mergeFinalScript.py $inputStory $rawStory $historyLines
python translateFile.py $rawStory $rawLines
python batch_tts.py $rawLines $voiceFolder
python imageAPI.py $rawLines $imageJsonFolder $stopwords
cp $historyLines $backupLines
python mergeJson.py $backupLines $rawLines $historyLines