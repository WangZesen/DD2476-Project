# script file for testing the res18 feature
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
import os
import json
import operator
import matplotlib.pyplot as plt

imgRootDir = '../images/'
# global setting for image normalization
scaler = transforms.Resize((224, 224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
to_tensor = transforms.ToTensor()

# def printDir():
#     print(imgRootDir)

def get_vector(image_name, torchModel):
    # 1. Load the image with Pillow library
    try:
        img = Image.open(image_name)
        # should only read in 3 channel images
        img = img.convert("RGB")
        # 2. Create a PyTorch Variable with the transformed image
        t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
        # 3. Create a vector of zeros that will hold our feature vector
        #    The 'avgpool' layer has an output size of 512
        my_embedding = torch.zeros(512)
        # 4. Define a function that will copy the output of a layer
        def copy_data(m, i, o):
            my_embedding.copy_(o.data)
        # 5. Attach that function to our selected layer
        h = layer.register_forward_hook(copy_data)
        # 6. Run the model on our transformed image
        torchModel(t_img)
        # 7. Detach our copy function from the layer
        h.remove()
        # 8. Return the feature vector
        return my_embedding
    except:
        print("no image, bad link")
        return [0]


def getNewRank(queryImgName, featJSON, idList, torchModel):
    # ResNet-18 expects images to be at least 224x224
    # as well as normalized with a specific mean and standard deviation.
    # So we will first define some PyTorch transforms:

    idList = [str(x) for x in idList]

    # get query vector
    vector1 = get_vector(queryImgName, torchModel).unsqueeze(0)
    # define cosine similarity
    cos = nn.CosineSimilarity(dim=1, eps=1e-6)

    disDict = {}
    for id in idList:
        # calculate cosine distance for each pair
        vector2 = torch.FloatTensor(featJSON[id]['feat']).unsqueeze(0)
        cos_sim = np.array(cos(vector1, vector2))
        # dist = np.dot(vector1,vector2)/(np.linalg.norm(vector1)*(np.linalg.norm(vector2)))
        # disDict.update({featJSON[id]['imgs']: cos_sim})
        disDict.update({featJSON[id]: cos_sim})

    # sort after reviewing all images vectors
    dcRank = sorted(disDict.items(), key=operator.itemgetter(1), reverse=True)
    idRank = [i[0] for i in dcRank]

    return idRank

if __name__ == '__main__':
    # Load the pretrained model
    examplemodel = models.resnet18(pretrained=True)
    # Use the model object to select the desired layer
    layer = examplemodel._modules.get('avgpool')
    # start eval mode
    examplemodel.eval()

    jsonfileroot = './images/featJSON.json'
    # read the json file for specific test class
    c = open(jsonfileroot, 'r')
    # decode to dictionary file
    featJSON = json.loads(c.read())
    c.close()

    idList = [0,1,2,3,4,5,6,7,8,9]
    queryImgName = '/Users/zhweng/Desktop/testQuery/class{}/test{}.jpg'

    idRank = getNewRank(queryImgName, featJSON, idList, examplemodel)
    print(idRank)
