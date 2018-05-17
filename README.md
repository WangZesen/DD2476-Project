# DD2476-Project: Shopping System with Craigslist Product

**Note:** The folder ***crawler*** is deprecated. All code are move into ***website*** folder.

## Project Main features:
- [x] Text Search Mode
- [x] Facets search
- [x] Search statistic
- [x] Spell check
- [x] Price interval, different rank rules, filter rules
- [x] Image Search Mode
- [x] Combination Search Mode: Text with Image
- [x] Smart Recommendation System

## Preparation

### 0 prerequisites
* Python 2.7
* Pytorch, torchvision
* Elasticsearch
And then install all the other python dependencies using pip:
```
pip install -r pip_list.txt
```

### 1 Craw the raw data without images

Use crawler.py to craw data from Craigslist website, totally 35 classes (~80,000 products) Files will be stored in website/data/ file. The raw data tar file is also provided.

### 2 Craw images with the help of mpi for speeding up
Use crawImages_mpi.py to craw the images and store in local computer. The download log is stored in downloadImages.log. The data will be stored in website/images/. The filtered new data json will be also generated and stored.

### 3 Extract CNN features using Resnet (Pytorch)
Use extractFeatureFinal.py. The features are stored [here](https://drive.google.com/file/d/1vHil721YsCCNFH7s7qPFcFGmmbvflCpk/view?usp=sharing). Put the file ***totalRes18feat.txt*** under website/

## Insert Data and run elasticsearch
Install all the python dependencies using pip:
```
python insert.py
elasticsearch # remember add PATH in ~/.bashrc
```

## Run the server
Link: [localhost:8080/](localhost:8080/)
```
python server.py
```

## Authorship

Ruiyang Ma, Zesen Wang, Zehang Weng, Zitao Zhang
