const puppeteer = require('puppeteer');
const fs = require('fs');
const util = require('util');

/*
const inFile = './test.html';
var fc = fs.readFileSync(inFile)

console.log(fc.toString());
var el = document.createElement( 'html' );

el.innerHTML = fc;
var hrefs = el.getElementsByTagName('a');
hrefs.forEach(a => {
  console.log(a.href);
});
*/

(async () => {
  const browser = await puppeteer.launch();
  console.log('User agent:')
  var userAgentValue = await browser.userAgent();
  console.log(userAgentValue);

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36')

  var target_url = 'http://www.chinadaily.com.cn/world/america'
  await page.goto(target_url, {waitUntil: 'load', timeout: 0});

  // Get the "viewport" of the page, as reported by the page.
  const feeds = await page.evaluate(target_url => {
    console.log('target_url = ', target_url);

    var targetAttr = document.createElement('a');
    targetAttr.href = target_url;
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
    /*console.log('href length:', hrefs.length);
    for(var i = 0; i < hrefs.length; i++) {
      console.log(hrefs[i].href)
    }*/
    return {
      links: links
    };
  }, target_url);

  var links = feeds['links'];
  console.log(util.format('Crawled total %d links.', links.length))

  var linkStart = 0;
  var linkEnd = links.length;

  for(var i = linkStart; i < linkEnd; i++) {
    var curUrl = links[i];
    console.log(util.format('[%d]current url: %s', i, curUrl))

    // Browse sub page of current website
    try{
      var res = await page.goto(curUrl, {waitUntil: 'load', timeout: 60000});
      console.log(res)
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

      var htmlContent = newsContent['content'];
      var fileName = util.format('./work/news/%d.html', i); 
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
})();
