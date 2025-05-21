import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load model
model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'trashnet_model.h5')
model = load_model(model_path)

# Kelas asli TrashNet
class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Fungsi prediksi
def predict_image(img_path):
    # Load & preprocess gambar
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    # Prediksi
    prediction = model.predict(img_array)
    predicted_index = np.argmax(prediction)
    predicted_class = class_names[predicted_index]

    # Mapping ke 2 kelas utama
    if predicted_class in ['paper', 'cardboard']:
        final_class = 'Organik'
    else:
        final_class = 'Anorganik'

    print(f"Hasil prediksi: {final_class} ({predicted_class})")
    return final_class, predicted_class
