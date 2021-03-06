from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
import os, sys, re, pdb, codecs, random
import json
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

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
    # Load Clients
    LoadClients()
    return JsonResponse(clientDict)

def news(request):
    template = loader.get_template('Archive/news.html')
    context = {}
    return HttpResponse(template.render(context, request))

def dream(request):
    global dreamIndex
    story = dreamList[dreamIndex]
    story = dreamList[(dreamIndex % len(dreamList))]
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
def updateClient(request):
    if request.method != 'GET':
        return HttpResponse('GET only')
    if 'name' not in request.GET:
        return HttpResponse('Client name not in query')
    name = request.GET['name']
    value = 0
    if 'value' in request.GET:
        try:
            value = int(request.GET['value'])
        except Exception:
            return HttpResponse('Invalid value')
    global clientDict
    clientDict[name] = value

    # Save to disk
    SaveClients()
    return JsonResponse(clientDict)

def clientStatus(request):
    return JsonResponse(clientDict)   

def removeClient(request):
    if request.method != 'GET':
        return HttpResponse('GET only')
    if 'name' not in request.GET:
        return HttpResponse('Client name not in query')
    name = request.GET['name']
    global clientDict
    if name in clientDict:
        try:
            del clientDict[name]
        except Exception:
            pass
        # Save to disk
        SaveClients()
        return HttpResponse('OK')
    return HttpResponse('Name not found')

def dreamClient(request):
    if request.method != 'GET':
        return HttpResponse('GET only')
    if 'name' not in request.GET:
        return HttpResponse('Client name not in query')
    name = request.GET['name']

    global clientDict
    story = dreamList[(clientDict[name] % len(dreamList))]
    clientDict[name] = (clientDict[name] + 1) % len(dreamList)
    return JsonResponse(story)    

def newsClient(request):
    if request.method != 'GET':
        return HttpResponse('GET only')
    if 'name' not in request.GET:
        return HttpResponse('Client name not in query')
    name = request.GET['name']
    if name not in clientDict:
        return HttpResponse('Client name doesn''t exist!')
    template = loader.get_template('Archive/clientView.html')
    context = {'name': name}
    return HttpResponse(template.render(context, request))
    
# Save & Load Client Info
def SaveClients():
    with codecs.open('./edream-client-info.json', 'w', 'utf8') as fout:
        json.dump(clientDict, fout, indent = 4, ensure_ascii = False)
        logging.debug('Saved client info({} clients)'.format(len(clientDict)))

def LoadClients():
    jsonPath = './edream-client-info.json'
    if os.path.exists(jsonPath) == False:
        return None
    global clientDict
    with codecs.open(jsonPath, 'r', 'utf8') as fin:
        clientDict = json.load(fin)
        logging.debug('Loaded client info({} clients)'.format(len(clientDict)))

