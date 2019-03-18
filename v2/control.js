var bodyText = ["The smaller your reality, the more convinced you are that you know everything.", "If the facts don't fit the theory, change the facts.", "The past has no power over the present moment.", "This, too, will pass.", "</p><p>You will not be punished for your anger, you will be punished by your anger.", "Peace comes from within. Do not seek it without.", "<h3>Heading</h3><p>The most important moment of your life is now. The most important person in your life is the one you are with now, and the most important activity in your life is the one you are involved with now."]
function generateText(sentenceCount) {
    for (var i = 0; i < sentenceCount; i++)
        document.write(bodyText[Math.floor(Math.random() * 7)] + " ")
}
rep = 0
var dreamIndex = 0

function readcaption() {
    // console.log('timing event', rep);

    var button = document.getElementById('main-btn-div');
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
  var lines = d3.json("lines/clean-lines.json",
  function(err, c1){
  })

  var r1 = lines.then(function(lineJson){
    var currentLine = lineJson[dreamIndex]
    console.log(currentLine)
    n = lineJson.length
    console.log(n)
    dreamIndex = (dreamIndex + 1) % n

    var res = d3.json("image-json/" + currentLine[2] + ".json",function(err, c1){})
    var voicePath = "voices/" + currentLine[2] + ".mp3"
    var r2 = res.then(function(dream){
      renderDream(currentLine[0], currentLine[1], dream, voicePath)
    })
  })

  //window.setTimeout(ReadDream, 6000);

}

function renderDream(en, zh, dream, voicePath) {
  // Image
  ImageReposition(dream.value[0]);
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
      window.setTimeout(ReadDream, 100);
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

function ImageReposition(imageinfo) {

    var img = document.getElementById('MainImg1');
    img.src = imageinfo.thumbnailUrl;
    //img.src = 'https://tse2.mm.bing.net/th?id=OIP.WgaQqMxxicDuNPbPKzfakgAAAA&pid=Api';
    // Image size
    height = imageinfo.thumbnail.height;
    width = imageinfo.thumbnail.width;

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

    console.log(img);
    img.style.marginLeft = mleft.toString() + "px";
    img.style.marginTop = mtop.toString() + "px";
    img.style.height = height.toString() + "px";
}
