#!/bin/bash -x
bash news-crawler/run_chrome_crawler.sh
bash model/train_model.sh
bash model/gen.sh