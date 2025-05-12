import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

# muat model sekali saat import
model_path = os.path.join(os.path.dirname(__file__), "..", "model", "trashnet_model.h5")
model = load_model(model_path)
# pastikan urutan label sesuai saat training
class_names = ['anorganik', 'organik']

def classify_image(img_path: str) -> str:
    img = image.load_img(img_path, target_size=(128, 128))
    arr = image.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, 0)
    preds = model.predict(arr)
    idx = int(np.argmax(preds[0]))
    return class_names[idx]
