# -*- coding: utf-8 -*-
"""Tester_load_data.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/151X3fOQKLmFXd1DldaN_2OXzxgBFyaWh

Reference from
 - code : https://colab.research.google.com/github/tensorflow/docs/blob/master/site/en/tutorials/images/classification.ipynb#scrollTo=jloGNS1MLx3A
 - data : https://www.kaggle.com/datasets/vencerlanz09/sea-animals-image-dataste?select=Turtle_Tortoise

### **Import Library**
"""

#import libary
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.datasets import mnist         # Grapth
from tensorflow.keras.models import Sequential      # model
from tensorflow.keras import layers
from tensorflow.keras.layers import Dense, Activation, Flatten, Dropout   # use command in model
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator   # resharp image
import pandas as pd
import matplotlib.pyplot as plt                    # run show grapth
import math
import numpy as np
import cv2                                      #pip3 install opencv-python
import urllib                                   # link into colab
import PIL                                     #  config detail image
import seaborn as sns                          # type grapth
from glob import glob                         # read file surname

from google.colab import drive  #google colab connect to goole drive
drive.mount('/content/drive')

"""### **DOWNLOAD FILE FROM (GOOGLE-DRIVE TO GOOGLE COLAB)**"""

!gdown --id 1eSJOT1kfftuwOHFFgrWBBo4AF6c0Jj4J

!cp '/content/drive/MyDrive/Kaggle/kaggle.json' '/content' #download file .json to drive

import zipfile
import os

os.environ['KAGGLE_CONFIG_DIR'] = "/content"

"""### **DOWNLOAD URL DATASET FROM KIGGLE**"""

!kaggle datasets download -d thapakornmeethangzr/test-data #api kaggle

zip_ref = zipfile.ZipFile('test-data.zip', 'r') #Opens the zip file in read mode
zip_ref.extractall('/content') #Extracts the files into the /tmp folder
zip_ref.close()

"""### **SELECT FILE PATH**"""

import pathlib

data_set = "/content/TestData"   #load image to data_set
image_count = len(os.listdir(data_set))

image_access = os.listdir(data_set)
dataAll_set = pathlib.Path(data_set)   #all image in dataAll_set(path)

image_count = len(list(dataAll_set.glob("*/*.jpg"))) #check
print(image_count)        #print amount of data

DF = pd.DataFrame(columns=['class','count'])
DF['class']=pd.Series([os.listdir(data_set)[x] for x in range(0,18)])
DF['count']=pd.Series([len(os.listdir(os.path.join(data_set,os.listdir(data_set)[x]))) for x in range(0,18)])
plt.figure(figsize=(8,6))
g=sns.barplot(x='class', y='count',data=DF)
g.set_xticklabels(g.get_xticklabels(), rotation=90)
plt.tight_layout()
#show Displays the amount of data in each class

plt.figure(figsize=(8,6))
plt.tight_layout()
plt.pie(DF['count'],
        labels=DF['class'],
        autopct='%1.1f%%')
plt.axis('equal')
plt.title('Proportion of each observed category')
plt.show()
#show Displays the amount of data in each class but circle

"""### TEST FILE **DATA**"""

ocean = list(dataAll_set.glob("Sharks/*"))
PIL.Image.open(str(ocean[55]))
#PIL.Image.open(str(ocean[125]))
#Example image in the data

"""### **CONFIGURATION**"""

# Define some parameter
batch_size = 16  # input data size
img_height = 64   # image height 128 pixel
img_width = 64   # image width 128 pixel

train_ds = tf.keras.utils.image_dataset_from_directory(
  dataAll_set,
  validation_split=0.55,                                                 #Separate validation set 45% dodge
  subset="training",                                                     #let this dataset be training
  seed=123,                                                              #This is so that the result of a randomly split data set doesn't change much each time the code is run.
  image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
  dataAll_set,
  validation_split=0.45,                                               #Separate validation set 55% dodge
  subset="validation",                                                 #let this dataset be validation
  seed=123,                                                            #This is so that the result of a randomly split data set doesn't change much each time the code is run.
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_name = train_ds.class_names
print(class_name)    #print all class name

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
  for i in range(8):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_name[labels[i]])
    plt.axis("off")
    #Example image in the class quantity 8 image

for image_batch, labels_batch in train_ds:
  print(image_batch.shape)
  print(labels_batch.shape)
  break

AUTOTUNE = tf.data.AUTOTUNE    #Parameters in batch number, which TensorFlow will handle appropriate amounts.

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)   #while the model is training We can read the data in the next batch without having to wait for the model to finish training first.
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)               #same as above line

normalization_layer = layers.Rescaling(1./255)  # rescale max 255 to 1 and 0 to 0

"""### **CONFIGURATION MODEL**"""

# Keras Model
num_class = len(class_name)

model = Sequential([
  layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),

  #layer(hidden)  .Conv2D('flatter', 'channal' , padding='same = ', activation='relu')
  #same = Forces this class to export data of the same size.
  #relu = is to "pass off" the linear function by choosing to turn off some neurons completely if the neuron is low.
  # .MaxPooling = Reduce the size of the tiles in the hidden layer.
  #Dropout = drop data 1 = 100%
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Dropout(0.5),

  layers.Conv2D(128, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Dropout(0.5),

  #.Flatten = It is intended to convert data from multiple channel images into vectors. that we can pass on to the standard MLP layer
  layers.Flatten(),

    # .Dense is fully connected or connect each and every node of one layer to another layer
  layers.Dense(128, activation='relu'),
  layers.Dense(num_class),

])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'],)

"""### SHOW DETAIL PARAMETER, LAYER"""

model.summary()  #show overall

"""### Process Train Model"""

history = model.fit(
  train_ds,                      #train data
  validation_data=val_ds, #test data
  epochs=15,                 #Number of cycles for train and test
  verbose=1,                  #display format the training progress for each epoch
  validation_split=0.2      #drop 20 percent off
)

"""### SHOW RESULT (GRAPTH)"""

err_hist = history.history
pd.DataFrame(err_hist).plot(figsize=(8, 5))
plt.grid(True)
plt.gca().set_ylim(0, 3.6) # set the vertical range to [0-1]
plt.show()

score = model.evaluate(train_ds, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', 100*score[1])

#test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Abbott%27s_Booby.jpg/800px-Abbott%27s_Booby.jpg"
#test_image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmRdQ56h4E8Ub6qJej1mgrFxS2YtVl8f2lHYkncNk0C-wgjQcQPyUGSYoVC7o0PYJ_VIk&usqp=CAU"
test_image_url = "https://www.cabq.gov/artsculture/biopark/news/10-cool-facts-about-penguins/@@images/1a36b305-412d-405e-a38b-0947ce6709ba.jpeg"
#test_image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTswrTmk8h-q27Fn9gxZbqh3nwsDu_-fQGiWw&usqp=CAU"
test_image_path = tf.keras.utils.get_file(origin=test_image_url)

req = urllib.request.urlopen(test_image_url)
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)
img2 = cv2.resize(img,[128,128])

plt.imshow(img2)
plt.show()

img = tf.keras.utils.load_img(
    test_image_path, target_size=(img_height, img_width)
)
img_array = tf.keras.utils.img_to_array(img)
img_array = tf.expand_dims(img_array, 0) # Create a batch

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
    .format(class_name[np.argmax(score)], 100 * np.max(score))
)