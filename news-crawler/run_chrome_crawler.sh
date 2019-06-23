!/bin/bash -x
cd $E_DREAM_ROOT
cd news-crawler
node crawlTask \
-urlFile './newsUrlList.txt' \
-outputFolder './work'