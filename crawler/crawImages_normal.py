import json
import wget
import os
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD



rawcrawDir = './data/'
outputGuide = os.listdir(rawcrawDir)
imgRootDir = './images/'
recordCrawImg = 'recordCrawImg.json'

missingRequest = 0
totalRequest = 0

for i in range(len(outputGuide)):
    # test
    i = 10

    guidefile = outputGuide[i]
    classLabel = guidefile.split('.')[0]
    # create the directory if path do not exist
    subImgDir = './images/{}/'.format(classLabel)
    if os.path.exists(subImgDir) is False:
        os.mkdir(subImgDir)
    # read the file with image links
    c=open(rawcrawDir + guidefile,'r')
    # decode to dictionary file
    data = json.loads(c.read())
    
    # 
    for j in range(len(data)):
        totalRequest = totalRequest + 1
        # slow, may change not to use out option to speed up
        try:
            filename = wget.download(data[j]['imgs'][0]['url'], out=subImgDir)
            data[j]['imgs'] = filename
        except:
            print('do not found image')
            missingRequest = missingRequest + 1
            # set to zero
            data[j]['imgs'] = 0

    # create the new json file
    f = open("{}newoutput{}.txt".format(imgRootDir, i), "w")
    f.write(json.dumps(data))
    f.close()

    # test for the first class
    break
print("download: {},  missing : {}".format(totalRequest, missingRequest))