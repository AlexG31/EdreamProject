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
lines.slice(0,4).forEach(l => {
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
      fs.mkdirSync(folderPath);

      // Start crawl
      crawl.crawl(l, folderPath)
    }
  }
});
