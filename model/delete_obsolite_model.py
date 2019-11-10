#encoding:utf8
import os, sys, re, pdb, glob

pat = re.compile(r'model-([0-9]+)')
def findModels(model_folder):
    models = dict()
    files = []
    files.extend(glob.glob(os.path.join(model_folder, 'model-[0-9]*.meta')))
    files.extend(glob.glob(os.path.join(model_folder, 'model-[0-9]*.index')))
    files.extend(glob.glob(os.path.join(model_folder, 'model-[0-9]*.data-*')))
    print('total number of model files: {}'.format(files))
    for p in files:
        name = os.path.split(p)[-1].split('.')[0]
        model_id = int(pat.match(name).group(1))
        if model_id not in models:
            models[model_id] = list()
        models[model_id].append(p)
    return models

def findObsoleteModels(models, topk = 30):
    model_id_list = list(models.keys())
    model_id_list.sort(reverse = True)
    print('models to keep: {}'.format(model_id_list[:3]))
    files = []
    for obs in model_id_list[3:]:
        files.extend(models[obs])
    return files

def deleteFiles(files):
    for p in files:
        print('remove: {}'.format(p))
        os.remove(p)

if __name__ == '__main__':
    models = findModels('./')
    obsolete = findObsoleteModels(models)
    deleteFiles(obsolete)