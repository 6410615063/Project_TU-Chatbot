import codecs, json, pickle
from sklearn.linear_model import ElasticNet
from pythainlp.word_vector import WordVector
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

class SecurityModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.wv = WordVector()
        self.model_path = os.path.join(os.path.dirname(__file__), 'models/finalized_model.sav')
        self.train_data_path = os.path.join(os.path.dirname(__file__), 'splits/train.json')
        self.test_data_path = os.path.join(os.path.dirname(__file__), 'splits/test.json')

    def load_dataset(self, fname):
        fp = codecs.open(fname, encoding="utf-8") 
        data = json.load(fp)
        return data

    def create_input_and_label(self, data):
        X = []
        Y = []
        
        for sample in data:
            text = sample[0].replace(" ", "")
            x = self.wv.sentence_vectorizer(text, use_mean=True)
            X.append(x[0])
            Y.append(0.9 if sample[1] == "unsafe" else 0.1)
            
        return np.array(X), np.array(Y)

    def build_model(self, x, y):
        print("Fitting....")
        regr = ElasticNet(alpha=0.001, max_iter=10000, random_state=0, selection="random")
        
        self.scaler.fit(x)
        new_x = self.scaler.transform(x)
        
        regr.fit(new_x, y)
        print("Fitting completed")
        return regr

    def train(self):
        train_data = self.load_dataset(self.train_data_path)
        X, Y = self.create_input_and_label(train_data)
        self.model = self.build_model(X, Y)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        pickle.dump([self.scaler, self.model], open(self.model_path, 'wb'))
        return self.model

    def load_model(self):
        if os.path.exists(self.model_path):
            self.scaler, self.model = pickle.load(open(self.model_path, "rb"))
            return True
        return False

    def predict(self, text):
        if not self.model:
            if not self.load_model():
                raise Exception("Model not trained. Please train the model first.")
        
        text = text.replace(" ", "")
        x = self.wv.sentence_vectorizer(text, use_mean=True)
        x = self.scaler.transform(x)
        out = self.model.predict(x)
        return "unsafe" if out[0] > 0.5 else "safe"

    def evaluate(self):
        test_data = self.load_dataset(self.test_data_path)
        count = 0
        
        for sample in test_data:
            text = sample[0]
            prediction = self.predict(text)
            if sample[1] == prediction:
                count += 1
                
        accuracy = count / len(test_data)
        return accuracy 