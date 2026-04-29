import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

class OmniBERTopic:
    def __init__(self, n_topics=10):
        self.n_topics = n_topics
        self.vectorizer = CountVectorizer(stop_words='english')
        
    def c_tf_idf(self, documents, m):
        X = self.vectorizer.fit_transform(documents)
        # Class-based TF-IDF math
        t = X.toarray()
        tf = np.divide(t, t.sum(axis=1, keepdims=True) + 1e-9)
        idf = np.log((m / t.sum(axis=0)) + 1)
        return tf * idf

    def fit_transform(self, documents):
        m = len(documents)
        return self.c_tf_idf(documents, m)

if __name__ == "__main__":
    docs = ["machine learning is great", "ai agents perform tasks", "deep learning models"]
    model = OmniBERTopic()
    matrix = model.fit_transform(docs)
    print(f"c-TF-IDF shape: {matrix.shape}")
