# ColourChem  
**AI-Powered Hair Analysis and Colour Prediction System**

---

## Overview  
ColourChem is a web-based application designed to assist professional hair stylists in predicting hair dye outcomes and assessing hair damage. The system integrates artificial intelligence with modern web technologies to reduce uncertainty in hair colouring processes while prioritising hair integrity.

The application provides tools for damage assessment, strand test prediction, formula tracking, and client management within a centralized platform.

---

## Features  

### AI Damage Assessment  
- Uses a convolutional neural network (CNN) model to analyse uploaded hair images  
- Predicts hair condition and potential damage levels  
- Assists stylists in making safer treatment decisions  

### Strand Test Prediction  
- Simulates possible outcomes of hair dye applications  
- Reduces the need for repeated physical strand testing  

### Client Management  
- Store and manage client profiles  
- Track session history and treatments   

### Formula Archive  
- Save and retrieve hair dye formulas  
- Reuse successful treatments  
- Improve consistency across sessions  

### Developer Volume Calculator  
- Calculates appropriate developer strength  
- Supports accurate chemical mixing decisions  

### Cloud Image Storage  
- Uses AWS S3 for storing uploaded images  
- Ensures scalability and reliable file management  

---

## Technology Stack  

### Frontend  
- HTML, CSS, JavaScript    

### Backend  
- Python  
- Flask  

### Database  
- MySQL  
- SQLAlchemy ORM  

### Artificial Intelligence  
- TensorFlow / Keras  
- Convolutional Neural Networks (CNN)  
- ResNet-based architecture  

### Cloud Services  
- Amazon Web Services (AWS S3)  

---

## System Architecture  

The application follows a modular architecture consisting of:

- Frontend Layer – User interface and interaction  
- Backend Layer – API routes and business logic  
- AI Module – Image preprocessing and prediction  
- Database Layer – Structured data storage  
- Cloud Storage – External image hosting  

---

## Installation  

### Prerequisites  
- Python 3.8+  
- MySQL  
- Virtual environment tool  

---

### Setup Instructions  

1. Clone the repository:
```bash
git clone https://github.com/Ray-Sydonia/Capstone-Project.git
cd Capstone-Project

2. Create and activate virtual environment:
```bash
$ python -m venv venv 
$ source venv/bin/activate (or .\venv\Scripts\activate on Windows)
$ pip install -r requirements.txt

3. Create a .env file:
```bash
SECRET_KEY=your_secret_key
DATABASE_URI=your_database_uri
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
S3_BUCKET_NAME=your_bucket

4. Run the application:
```bash
python run.py

5. Open in browser:
```bash
http://127.0.0.1:5000