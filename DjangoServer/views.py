from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
import os, sys, re, pdb, codecs, random
import json

def LoadGan():
    dreamList = []
    # dreamFilePath = 'talk/data/gan2_out.txt'
    # with codecs.open(dreamFilePath, 'r', 'utf8') as fin:
        # for line in fin:
            # dreamList.append(line.strip())
    dreamFilePath = '/home/alex/web/nginx/static/v2/dream.json'
    static_folder = 'http://139.199.32.181:9002/v2/'
    with codecs.open(dreamFilePath, 'r', 'utf8') as fin:
        dreamList = json.load(fin)
        for ind in range(len(dreamList)):
            dreamList[ind]['speechpath'] = '{}/{}'.format(
                    static_folder,
                    os.path.split(dreamList[ind]['speechpath'])[-1])
    #random.shuffle(dreamList)
    return dreamList
# Global Dreams
dreamList = LoadGan()
dreamIndex = 0
clientDict = dict()

# Create your views here.
def index(request):
    template = loader.get_template('talk/index.html')
    context = {
        'latest_question_list': ['ok', 'gpf'],
    }
    return HttpResponse(template.render(context, request))

def news(request):
    template = loader.get_template('Archive/news.html')
    context = {}
    return HttpResponse(template.render(context, request))

def dream(request):
    global dreamIndex
    story = dreamList[dreamIndex]
    dreamIndex = (dreamIndex + 1) % len(dreamList)
    return JsonResponse(story)    
    
def reload(request):
    global dreamIndex
    global dreamList
    dreamList = LoadGan()
    dreamIndex = 0

    #Non-empty imagejson
    image_count = 0
    for dream in dreamList:
        if 'imagejson' in dream and len(dream['imagejson']) > 0:
            image_count += 1
    return JsonResponse({'Reload Dream Size':len(dreamList),
        'Story with image': image_count})    

# Client API
def updateClient(name, value = 0):
    if request.method != 'GET':
        return HttpResponse('GET only')
    if name not in request.GET:
        return HttpResponse('Client name doesn''t exist!')
    name = request.GET['name']
    value = 0
    if 'value' in request.GET:
        try:
            value = int(request.GET['value'])
        except Exception:
            return HttpResponse('Invalid value')
    global clientDict
    clientDict[name] = value
    return JsonResponse(clientDict)

def clientStatus(request):
    return JsonResponse(clientDict)   

def removeClient(request):
    if request.method != 'GET':
        return HttpResponse('GET only')
    if name not in request.GET:
        return HttpResponse('Client name doesn''t exist!')
    name = request.GET['name']
    global clientDict
    if name in clientDict:
        try:
            del clientDict[name]
        except Exception:
            pass
        return HttpResponse('OK')
    return HttpResponse('Name not found')

def dreamClient(request):
    if request.method != 'GET':
        return HttpResponse('GET only')
    if name not in request.GET:
        return HttpResponse('Client name doesn''t exist!')
    name = request.GET['name']

    global clientDict
    story = dreamList[clientDict[name]]
    clientDict[name] = (clientDict[name] + 1) % len(dreamList)
    return JsonResponse(story)    
    
    
