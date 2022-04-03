from tensorflow import keras
import tensorflow_addons as tfa
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np

MODEL_CO = keras.models.load_model('model_CO.h5')

file_name = "/home/cotrack/CoTrack-Web-mvps/media/127_2_3.png"

rimg = load_img(file_name,target_size=(72,185))
new_X = (img_to_array(rimg))
n = new_X.reshape((1,72,185,3))

print(MODEL_CO.predict(n))
