const puppeteer = require('puppeteer');
const fs = require('fs');
const util = require('util');
const crypto = require('crypto');
const hashMethod = 'md5';

exports.hello = function (name) {
  console.log('hello world!', name)
  return 100;
}

exports.crawl = async function (targetUrl, saveFolder) {
  if (!fs.existsSync(saveFolder)) throw new Exception('save folder does not exist: ' + saveFolder);

  const browser = await puppeteer.launch({args: ['--no-sandbox']});
  console.log('User agent:');
  var userAgentValue = await browser.userAgent();
  console.log(userAgentValue);

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36')

  try {
    await page.goto(targetUrl, {waitUntil: 'load', timeout: 100000});
  } catch (err) {
    console.log('target url:', targetUrl)
    console.log('goto has error:', err)
  }
  // Get the "viewport" of the page, as reported by the page.
  const feeds = await page.evaluate(targetUrl => {
    console.log('target url = ', targetUrl);

    var targetAttr = document.createElement('a');
    targetAttr.href = targetUrl;
    var targetHost = targetAttr.hostname.toString();

    console.log('target host = ', targetHost);

    var hrefs = document.getElementsByTagName('a');
    var links = Array();
    for(var i = 0; i < hrefs.length; i++) {
      var curUrl = hrefs[i].href;
      var curHost = hrefs[i].hostname.toString();
      if (curHost != targetHost) continue;

      var slashIndex = curUrl.lastIndexOf('/');
      if (slashIndex == -1) continue;
      var pageUrlName = curUrl.substr(slashIndex + 1);
      var matchResult = pageUrlName.match(/[\#\?]+/);
      if (matchResult) continue;
      // match year in url
      if (!curUrl.match(/([\d]{4})/)) continue;

      links.push(curUrl);
    }
    return {
      links: links
    };
  }, targetUrl);

  var links = feeds['links'];
  console.log(util.format('Crawled total %d links.', links.length))

  var linkStart = 0;
  var linkEnd = links.length;

  for(var i = linkStart; i < linkEnd; i++) {
    var curUrl = links[i];
    console.log(util.format('[%d]current url: %s', i, curUrl))

    // Browse sub page of current website
    try{
      await page.goto(curUrl, {waitUntil: 'load', timeout: 60000});
    }
    catch (err) {
      console.log("sub page crawling error:", err)
      continue;
    }

    // Get the "viewport" of the page, as reported by the page.
    try {
      const newsContent = await page.evaluate(() => {
        var passages = document.getElementsByTagName('p');
        var content = Array();
        for (var j = 0; j < passages.length; j++) {
          content.push(passages[j].innerText);
        }
        
        return {
          'content': content.join('\n')
        };
      });

      // Write curUrl to first line of the file
      var htmlContent = curUrl + '\n' + newsContent['content'];
      var hash = crypto.createHash(hashMethod);
      hash.update(curUrl);
      var hashFileName = hash.digest('hex').toString();
      var saveHtmlPath = util.format('%s/%s.html', saveFolder, hashFileName);
      console.log('Save html content to ', saveHtmlPath);
      var fileName = saveHtmlPath; 
      fs.writeFile(fileName, htmlContent, function(err) {
          if(err) {
            return console.log(err);
          }

          console.log(util.format("The file %s was saved!", fileName));
      }); 
    } catch(err) {
      console.log(err)
      continue;
    }
    
  }
  
  await browser.close();

}
