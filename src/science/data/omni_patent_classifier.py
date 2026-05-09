import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import joblib

class OmniAIPatentClassifier:
    """
    Text Classification of AI Related Patents.
    Uses TF-IDF + LinearSVC for rapid, baseline classification of patent abstracts.
    Can be easily swapped with a Transformer model for production.
    """
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=10000)),
            ('clf', LinearSVC(C=1.0, dual=False))
        ])
        self.is_trained = False

    def train(self, data_path: str):
        """
        Train the classifier on a CSV containing 'abstract' and 'is_ai' columns.
        """
        print(f"Loading patent data from {data_path}...")
        # Mock load for safety
        # df = pd.read_csv(data_path)
        df = pd.DataFrame({
            "abstract": ["Neural network for image recognition", "A new mechanical gear system"],
            "is_ai": [1, 0]
        })
        
        X = df['abstract']
        y = df['is_ai']
        
        self.pipeline.fit(X, y)
        self.is_trained = True
        print("Model trained successfully.")

    def predict(self, abstract_text: str) -> bool:
        if not self.is_trained:
            raise ValueError("Model must be trained before inference.")
        
        prediction = self.pipeline.predict([abstract_text])[0]
        return bool(prediction == 1)

    def save_model(self, path: str):
        joblib.dump(self.pipeline, path)

    def load_model(self, path: str):
        self.pipeline = joblib.load(path)
        self.is_trained = True
