# use resnet 18 average pooling feature as feature vector

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
import os
import json


def get_vector(image_name):
    # 1. Load the image with Pillow library
    try:
        # print(image_name)
        img = Image.open(image_name)
        # should only read in 3 channel images
        img = img.convert("RGB")
        # 2. Create a PyTorch Variable with the transformed image
        t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
        # 3. Create a vector of zeros that will hold our feature vector
        # The 'avgpool' layer has an output size of 512 for resnet18
        my_embedding = torch.zeros(512)
        # # 2048 for resnet50
        # my_embedding = torch.zeros(2048)

        # 4. Define a function that will copy the output of a layer
        def copy_data(m, i, o):
            my_embedding.copy_(o.data)
        # 5. Attach that function to our selected layer
        h = layer.register_forward_hook(copy_data)
        # 6. Run the model on our transformed image
        model(t_img)
        # 7. Detach our copy function from the layer
        h.remove()
        # 8. Return the feature vector
        return my_embedding
    except:
        print("no image, bad link")
        return [0]

#
# def SPPpooling():
#     # do an extra SPP pooling after average pooling
#     pass

imgRootDir = './images/'

# Load the pretrained model
model = models.resnet18(pretrained=True)
# model = models.resnet50(pretrained=True) # remember to change the size of vec

# Use the model object to select the desired layer
layer = model._modules.get('avgpool')
# start eval mode
model.eval()

# ResNet-18 expects images to be at least 224x224
# as well as normalized with a specific mean and standard deviation.
#  So we will first define some PyTorch transforms:
scaler = transforms.Resize((224, 224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
to_tensor = transforms.ToTensor()


# for each class
feat_json = {}

counter = 0
for classid in range(35):
    # classid=6
    print("start extract features for class {}.".format(classid))
    guidefile = "{}new_output{}.txt".format(imgRootDir,classid)
    c=open(guidefile,'r')
    # decode to dictionary file
    data = json.loads(c.read())
    c.close()

    # for each item in one class
    for j in range(len(data)):
        imgid = data[j]['pid']
        imgdir = data[j]['imgs']
        feat_vec = list(get_vector(imgdir))
        feat_json.update({imgid:{'imgdir':imgdir,'feat':feat_vec}})

        counter = counter + 1
        if counter%10 == 0:
            print("complete extract {} features.".format(counter))
    # break

# create the new json file
f = open("./totalRes18feat.txt".format(imgRootDir), "w")
f.write(json.dumps(feat_json))
f.close()
print("finish extract features for class {}.".format(classid))

print("finish extract features for all classes.")