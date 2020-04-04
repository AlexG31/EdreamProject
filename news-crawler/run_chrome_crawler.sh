#!/bin/bash -x
#E_DREAM_ROOT='/media/alexg/vol1/github/EdreamProject'
E_DREAM_ROOT='/home/alexg/github/EdreamProject'
cd $E_DREAM_ROOT
cd news-crawler
dateFileName="`date -I`"
dailyFolder="./work/$dateFileName"
mkdir -p "$dailyFolder"
chmod 777 "$dailyFolder"
node crawlTask \
--urlFile './newsUrlList.txt' \
--outputFolder './work' \
> "./work/$dateFileName.log" 2>&1

echo "=====Let's Merge Them!====="
python3 $E_DREAM_ROOT/util/merge_data_util.py \
'./work' \
"./work/$dateFileName.merged.txt" 