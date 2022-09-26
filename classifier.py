import fasttext
import string
from enum import Enum

def train_model():
    model = fasttext.train_supervised('utterances.txt', epoch=100)
    model.save_model('classification_model.bin')

model = fasttext.load_model('classification_model.bin')
#print(model.words)
#print(model.labels)
print('Classification model', model)

def cleanup(text):
    return text.translate(str.maketrans('', '', string.punctuation)).lower()

class Labels(Enum):
    HELP = 'help'
    ETHEREUM = 'ethereum'
    TEMPERATURE = 'temperature'
    
def predict(text):
    labels, scores = model.predict(cleanup(text))
    label = Labels(labels[0].split('__')[-1])
    score = scores[0]
    return label, score