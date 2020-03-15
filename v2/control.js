var bodyText = ["The smaller your reality, the more convinced you are that you know everything.", "If the facts don't fit the theory, change the facts.", "The past has no power over the present moment.", "This, too, will pass.", "</p><p>You will not be punished for your anger, you will be punished by your anger.", "Peace comes from within. Do not seek it without.", "<h3>Heading</h3><p>The most important moment of your life is now. The most important person in your life is the one you are with now, and the most important activity in your life is the one you are involved with now."]
function generateText(sentenceCount) {
    for (var i = 0; i < sentenceCount; i++)
        document.write(bodyText[Math.floor(Math.random() * 7)] + " ")
}
rep = 0;
var dreamIndex = Math.floor(Math.random() * 10000);
var preloadImageObject = Array(null, null);
var playGap = 1000;

function readcaption() {
    // console.log('timing event', rep);

    var button = document.getElementById('main-btn');
    button.style.display = 'none';
    document.getElementById('image-container').style.display = 'block';
    document.getElementById('storytext-container').style.display = 'block';

    ReadDream();

}

function PlaySpeech(speechpath) {
     var teller = document.getElementById('teller');
     teller.src = speechpath;

     teller.play();
     return teller;
}

function ReadDream() {

  // lines
  var lines = d3.json("lines/clean-lines.json")

  var r1 = lines.then(function(lineJson){
    n = lineJson.length
    console.log('total lines in story:', n)
    dreamIndex = dreamIndex % n
    var currentLine = lineJson[dreamIndex]
    dreamIndex = (dreamIndex + 1) % n

    // Preload Image
    nextIndex = dreamIndex
    
    var fileExists = UrlExists("image-json/" + currentLine[2] + ".json");
    preloadImage(lineJson, nextIndex)
    if (fileExists) {
      var res = d3.json("image-json/" + currentLine[2] + ".json")
      var voicePath = "voices/" + currentLine[2] + ".mp3"
      console.log(voicePath)
      var r2 = res.then(function(dream){
        renderDream(currentLine[0], currentLine[1], dream, voicePath)
      })
    } else {
      //renderDream(currentLine[0], currentLine[1], null, voicePath)
      window.setTimeout(ReadDream, playGap);
    }

  })

  //window.setTimeout(ReadDream, 6000);

}

function preloadImage(lineJson, nextIndex) {
  var currentLine = lineJson[nextIndex]

  var fileExists = UrlExists("image-json/" + currentLine[2] + ".json");
  console.log('file? ->', fileExists);
  if (fileExists) {
    var res = d3.json("image-json/" + currentLine[2] + ".json")
    var r2 = res.then(function(dream){
      var p1 = "images/image-not-found.jpg"
      if (dream != null) {
        p1 = dream.value[0].thumbnailUrl;
      }

      console.log('preload image url: ', p1);
      var pd = preloadImageObject[nextIndex % 2];
      pd = new Image();
      pd.src = p1;
      pd.id = "MainImg1"

    })
  } else {
    preloadImageObject[nextIndex % 2] = new Image();
    preloadImageObject[nextIndex % 2].src = "images/image-not-found.jpg";
    preloadImageObject[nextIndex % 2].id = "MainImg1";
  }
}

function UrlExists(url)
{
    var http = new XMLHttpRequest();
    http.open('HEAD', url, false);
    http.send();
    return http.status!=404;
}

function renderDream(en, zh, dream, voicePath) {
  if (dream != null) {
    var height = dream.value[0].thumbnail.height;
    var width = dream.value[0].thumbnail.width;
    var p1 = dream.value[0].thumbnailUrl
    console.log('Loading current image:', p1)
    ImageReposition(p1, width, height);

  } else {
    // random choose default image
    default_image_count = 6
    default_image_index = 1 + getRandomInt(default_image_count)
    default_image_path = `images/color-${default_image_index}.jpg`
    console.log(`using default image ${default_image_path}`)
    //defaultImage = 'images/image-not-found.jpg'
    //var width = 450
    //var height = 450
    //ImageReposition(default_image_path, width, height);
    var img = document.getElementById('MainImg1');
    img.src = default_image_path
  }

  document.getElementById('MainImg1').style.height = "310px";

  // en
  document.getElementById('storytext').innerHTML = en;
  // zh
  document.getElementById('chinesestory').innerHTML = zh;

  // voice

  var speech = PlaySpeech(voicePath);
  //window.setTimeout(readcaption, 6000);
  speech.onended = function () {
      //console.log('Audio ended.')
      window.setTimeout(ReadDream, playGap);
  }
}

function calWrap() {
    var wrap, image_container, text_container;
    wrap = document.getElementsByClassName('wrap-container')[0];
    text_container = document.getElementsByClassName('text-container')[0];
    text_container.style.display = 'block';
    text_container.style.top = wrap.clientHeight + 90 + 'px';
    image_container = document.getElementsByClassName('image-container')[0];
    image_container.style.position = 'absolute';
    image_container.style.top = '50%';
    image_container.style.left = '50%';
    image_container.style.marginTop = -image_container.clientHeight / 2 + 'px';
    image_container.style.marginLeft = -image_container.clientWidth / 2 + 'px';
}

function ClipSize(height, width, max_height) {
    if (height > max_height) {
        nh = max_height;
        nw = width / height * max_height;

        height = nh;
        width = nw;
    }
    return {'height':height, 'width':width};
}

function ImageReposition(imagePath, width, height) {

  var cimage = preloadImageObject[(dreamIndex + 1) % 2];
  if (cimage == null) {
    document.getElementById('MainImg1').src = imagePath;
    console.log('preload image object is null!')
  } else {
    document.getElementById('MainImg1').remove();
    document.getElementById('image-container').appendChild(cimage);
    console.log('current image url:', imagePath);
    console.log('using preload image url:', cimage.src);
  }

  var img = document.getElementById('MainImg1');
  img.visibility = 'hidden';

  // Clip height
  new_size = ClipSize(height, width, 500);
  height = new_size.height;
  width = new_size.width;
  //height = 150;
  //width = 135;
  console.log('Width, height,', width, height);

  var WindowWidth = document.getElementById('image-container').clientWidth;
  console.log('WindowWidth:', WindowWidth);

  mleft = (WindowWidth - width) / 2;
  mtop = (500 - height) / 2;

  img.style.marginLeft = mleft.toString() + "px";
  img.style.marginTop = mtop.toString() + "px";
  img.style.height = height.toString() + "px";

  img.visibility = 'visible';
}


/*
* Convert image url to local image location
*/
function convertUrl2LocalPath(imageinfo, action) {
  var url = imageinfo.contentUrl
  var thumbnailUrl = imageinfo.thumbnailUrl
  var ext = imageinfo.encodingFormat

  var imgHash = d3.json("images/image-hash.json")
  imgHash.then(function(hashJson){
      hashJson.forEach(function(v){
        if (v.url == url) {
          imgPath = 'images/' + v.hash + '.' + ext
          console.log('local image: ' + imgPath)
          action(imgPath)
        }
      })
    }
  )
}
function getRandomInt(max) {
  return Math.floor(Math.random() * Math.floor(max));
}