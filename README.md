# Twitter Sentiment Analysis
<h2>Let's experiance the project 👉👉👉 <a href="https://seintiment-analysis.onrender.com/" target="_blank">Application_demo</a></h2><br>
<div align="center">
  <h2>Lets Play Application Demo Video 👇👇 </h2>
  <a href="https://www.youtube.com/watch?v=LMgT02ONujQ" target="_blank">
        <img src="https://github.com/mayurdhoble/Full-Stack-Sentiment-Analysis-Application/blob/main/templates/ett.png?raw=true" alt="Application Demo Video" width="580" height="300">

  </a>
</div>


## Project Overview
This project implements a machine learning-based sentiment analysis system for Twitter reviews. It uses a Logistic Regression model trained on the Sentiment140 dataset to classify text as either positive or negative sentiment.

## Dataset Information
The model is trained on the Sentiment140 dataset which contains:
- 1.6 million tweets
- Binary sentiment classification (0 = negative, 1 = positive)
- Features include: target, ids, date, flag, user, and text

## Technical Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Machine Learning**: Scikit-learn, NLTK
- **Database**: SQLite

## Model Architecture
The sentiment analysis model uses:
- Text preprocessing and cleaning
- CountVectorizer for feature extraction
- Logistic Regression classifier
- Achieved accuracy: 78.39%

## API Usage
The sentiment analysis endpoint can be accessed via POST request:
```
POST /predict
Content-Type: application/x-www-form-urlencoded

Body: review=your_text_here
```
Response format:
```
{
    "prediction": "Positive/Negative",
    "status": "success"
}
```

## Features
- Real-time sentiment analysis
- User authentication system
- Responsive design
- Dark mode support
- Contact form functionality

## Installation
To run the project locally:
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the Flask application: `python app.py`
4. Access at: <a href="https://seintiment-analysis.onrender.com/" target="_blank">Application_demo</a>

## YouTube Video
This section will showcase the output of the project. You can watch the video [here](https://www.youtube.com/watch?v=LMgT02ONujQ).
