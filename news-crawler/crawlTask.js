const puppeteer = require('puppeteer');
const fs = require('fs');
const util = require('util');
const crawl = require('./crawl')
const crypto = require('crypto');
const hashMethod = 'md5';

const inFile = './newsUrlList.txt';
var fc = fs.readFileSync(inFile)

var lines = fc.toString().split('\n');
var hashDict = new Set();

(async ()=> {

for (var i = 5; i < 7; i++) {
  var l = lines[i];
  // Create url hash
  const hash = crypto.createHash(hashMethod);
  console.log(l);
  hash.update(l);
  var res = hash.digest('hex');
  var h = res.toString();
  console.log(h);

  if (hashDict.has(h)) {
    console.log("url already exists: ", l);
  } else {
    hashDict.add(h);
    var datetime = new Date();
    var folderPath = util.format('./work/%s/%s', datetime.toISOString().substr(0, 10), h);
    console.log('creating folder: ', folderPath);

    // Make dir
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath, {recursive: true});
    }

    // Start crawling
    try {
      await crawl.crawl(l, folderPath);
    } catch (err) {
      console.log(err);
    }
  }
};

})();
