#!/bin/bash -x
# Password: Edream2019gpf
bash news-crawler/run_chrome_crawler.sh
bash model/train_model.sh
bash model/gen.sh