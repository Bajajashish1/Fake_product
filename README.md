Fake Product Detection Using YOLOv8
1. Introduction

Counterfeit products have become a major issue in global markets, affecting both consumers and brand manufacturers. Fake products not only reduce brand value but can also harm consumer safety, especially in industries such as cosmetics, pharmaceuticals, electronics, and fashion. Traditional methods of detecting counterfeit products rely on manual inspection, which is time-consuming and often inaccurate.

With the advancement of Artificial Intelligence and Computer Vision, automated systems can now analyze product images and identify whether a product is authentic or counterfeit. This project proposes a deep learning–based fake product detection system using YOLOv8, which can detect and classify products in real time.

2. Problem Statement

The rapid increase in counterfeit products across online and offline markets makes it difficult for consumers and retailers to identify fake items. Manual verification methods are inefficient, and existing automated systems often lack accuracy and scalability.

Therefore, there is a need for a smart system that can automatically detect counterfeit products from images using deep learning techniques.

3. Objectives of the Project

The main objectives of the project are:

To develop an automated system for detecting fake products using deep learning.

To use YOLOv8 object detection model for accurate and fast product recognition.

To create a dataset of real and fake product images for training the model.

To improve detection accuracy through image preprocessing and data augmentation.

To enable real-time counterfeit product detection for consumers and businesses.

4. Technologies Used
Programming Language

Python

Deep Learning Framework

YOLOv8 (You Only Look Once Version 8)

Libraries

OpenCV

NumPy

Pandas

PyTorch

Ultralytics YOLO

Tools

Google Colab / Jupyter Notebook

Roboflow (for dataset annotation)

LabelImg (for bounding box labeling)

5. System Architecture

The system works in several stages:

Data Collection

Data Preprocessing

Image Annotation

Model Training using YOLOv8

Model Evaluation

Deployment and Prediction

The system takes an image as input and detects whether the product is original or counterfeit using trained deep learning models.

6. Working of the System
Step 1: Data Collection

Images of authentic and counterfeit products are collected from various sources such as:

Online marketplaces

Brand product catalogs

Image datasets

The dataset includes images taken under different lighting conditions, backgrounds, and angles.

Step 2: Data Preprocessing

The collected images undergo preprocessing to improve model performance.

Preprocessing steps include:

Image resizing (e.g., 640×640 pixels)

Noise reduction

Data augmentation (rotation, flipping, brightness adjustment)

These steps help the model learn better features.

Step 3: Image Annotation

Each image is labeled with bounding boxes indicating the location of the product.

Example classes:

Real Product

Fake Product

Annotation tools such as Roboflow or LabelImg are used to create YOLO format labels.

Step 4: Model Training

The YOLOv8 model is trained using the prepared dataset.

Training involves:

Loading the dataset

Applying pretrained YOLOv8 weights

Running multiple epochs

Adjusting hyperparameters

During training, the model learns to identify patterns that differentiate authentic products from counterfeit ones.

Step 5: Model Evaluation

After training, the model is tested using a validation dataset.

Evaluation metrics include:

Precision

Recall

F1 Score

Mean Average Precision (mAP)

These metrics help measure how accurately the model detects counterfeit products.

Step 6: Detection and Prediction

Once the model is trained, it can analyze new product images.

The system:

Accepts an image as input.

Detects objects using YOLOv8.

Draws bounding boxes around detected products.

Displays whether the product is real or fake with a confidence score.

7. Advantages of the Proposed System

High detection accuracy using YOLOv8.

Real-time object detection capability.

Can be integrated with mobile or web applications.

Reduces manual effort in identifying counterfeit products.

Helps protect consumers and brands from fraud.

8. Applications

The system can be used in:

E-commerce platforms

Retail stores

Brand authentication systems

Supply chain monitoring

Consumer product verification apps
