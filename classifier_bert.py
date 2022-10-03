import string
from enum import Enum
from transformers import AutoTokenizer, AutoModel
import torch
from torch import nn

MODEL_NAME = 'distilbert-base-uncased'

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

def to_device(batch):
    return {key: value.to(device) for key, value in batch.items()}

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(records):
    return tokenizer(records['text'], padding='max_length', truncation=True)

embedding_model = AutoModel.from_pretrained(MODEL_NAME).to(device)
embedding_model.eval()

def embed(input_ids, attention_mask, labels=None):
    with torch.no_grad():
        return embedding_model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state[:, 0, :]

classifier = torch.load('./classifier.bin').to(device)
classifier.eval()

print('Classification model', classifier)

class Labels(Enum):
    HELP = 'help'
    ETHEREUM = 'ethereum'
    TEMPERATURE = 'temperature'
    
LABELS = {
    0: Labels.TEMPERATURE,
    1: Labels.ETHEREUM,
    2: Labels.HELP
}
    
def predict(text):
    with torch.no_grad():
        tokens = tokenizer(text, padding='max_length', truncation=True, return_tensors='pt')
        tokens = to_device(tokens)
        embeddings = embed(**tokens)
        classes = nn.functional.softmax(classifier(embeddings), dim=-1)
    clazz = torch.argmax(classes).cpu().item()
    score = classes[0, clazz].cpu().item()
    label = LABELS[clazz]
    return label, score