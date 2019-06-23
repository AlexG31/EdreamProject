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
  const page = await browser.newPage();
  var target_url = 'http://www.chinadaily.com.cn/world/america'
  await page.goto(target_url);

  // Get the "viewport" of the page, as reported by the page.
  const feeds = await page.evaluate(() => {
    var targetAttr = document.createElement('a');
    targetAttr.href = target_url;
    var targetHost = targetAttr.hostname.toString();

    var hrefs = document.getElementsByTagName('a');
    var links = Array();
    var curUrl = hrefs[i].href;
    for(var i = 0; i < hrefs.length; i++) {
      var curHost = hrefs[i].hostname.toString();
      if (curHost != targetHost) continue;

      var slashIndex = curUrl.lastIndexOf('/');
      if (slashIndex == -1) continue;
      var pageUrlName = curUrl.substr(slashIndex + 1);
      var matchResult = pageUrlName.match(/[\#\?]+/);
      if (matchResult) continue;

      links.push(hrefs[i].href);
    }
    /*console.log('href length:', hrefs.length);
    for(var i = 0; i < hrefs.length; i++) {
      console.log(hrefs[i].href)
    }*/
    return {
      links: links
    };
  });

  var links = feeds['links'];
  console.log(util.format('Crawled total %d links.', links.length))

  var linkStart = 20;
  var linkEnd = 30;

  for(var i = linkStart; i < linkEnd; i++) {
    var curUrl = links[i];
    console.log(util.format('[%d]current url: %s', i, curUrl))

    // Browse sub page of current website
    try{
      var res = await page.goto(curUrl);
      console.log(res)
    }
    catch (err) {
      console.log("sub page crawling error:", err)
      continue;
    }

    // Get the "viewport" of the page, as reported by the page.
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
    
  }
  

  await browser.close();
})();
