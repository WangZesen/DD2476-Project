# /usr/bin/mpiexec -np 32 python crawImages_mpi.py
# /Users/zhweng/anaconda/bin/mpiexec -np 32 python crawImages_mpi.py
import json
import wget
import os
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

recv_data = None
if rank == 0:
    send_data = range(10)
    print("process {} scatter data {} to other processes".format(rank, send_data))
else:
    send_data = None

i = comm.scatter(send_data, root=0)

print("process {} start download {} class images ...".format(rank, recv_data))

rawcrawDir = './data/'
outputGuide = os.listdir(rawcrawDir)
imgRootDir = './images/'
recordCrawImg = 'recordCrawImg.json'

missingRequest = 0
totalRequest = 0


guidefile = outputGuide[i]
classLabel = guidefile.split('.')[0]
classID = classLabel[6:]
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
f = open("{}new_{}.txt".format(imgRootDir, classLabel), "w")
f.write(json.dumps(data))
f.close()

frecord = open("downloadImages.log","a")
frecord.write("Class {} ==> download: {},  missing : {}\n".format(classID, totalRequest, missingRequest))
frecord.close()