# 🩸 HemoScan – Non-Invasive Anemia Detection

HemoScan is a deep learning-based web application that estimates hemoglobin (Hb) levels from fingertip (nail-bed) images using a Convolutional Neural Network (CNN). The system enables non-invasive screening and real-time prediction with clinical interpretation.

---

## 🚀 Live Demo

👉 https://kripasajo-hemoscan.hf.space

---

## 🎯 Features

- Upload fingertip (nail-bed) images  
- CNN-based hemoglobin prediction using MobileNetV2  
- Anemia classification (Normal, Mild, Moderate, Severe)  
- Real-time prediction  
- Data storage using SQLite database  
- User-friendly interface built with Streamlit  

---

## 🧠 Model Details

- Architecture: MobileNetV2 (Transfer Learning)  
- Task: Regression (Hemoglobin prediction)  
- Loss Function: Huber Loss  
- Evaluation Metric: Mean Absolute Error (MAE)  

### Preprocessing Steps

- ROI extraction (nail-bed region)  
- Image resizing (224 × 224)  
- Normalization  
- Data augmentation (rotation, brightness)  

---

## ⚙️ Tech Stack

Python, TensorFlow, Keras, MobileNetV2, OpenCV, NumPy, Pandas, Streamlit, SQLite

---

## 🏗️ Project Structure
<img width="511" height="176" alt="image" src="https://github.com/user-attachments/assets/840f03c6-0b5f-454b-807f-c11ff1e08a2f" /n>



🌐 Deployment
This application is deployed using Hugging Face Spaces (Streamlit + Docker environment) and is accessible via a public web link.

⚠️ Disclaimer
This application is intended for research and preliminary screening only.
It is not a substitute for professional medical diagnosis.
