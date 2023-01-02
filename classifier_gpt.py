import openai
from labels import Labels
import os

openai.api_key = os.getenv('API_KEY')

def predict(text):
    prompt = f'''
The following classes with examples statements exist:
TEMPERATURE: 'How cold is it', 'Do I need to wear gloves', 'Will it snow', 'What is the weather like', 'Can I go skiing'
HELP: 'I need help', 'Support me', 'I am lost', 'I do not understand this'
ETHEREUM: 'Am I rich', 'How much money do I have', 'Can I buy a new car', 'Can I retire yet', 'Cash', 'Virtual money', 'Ethereum'
CAMERA: 'Show me my appartment', 'Is there someone', 'Security feed', 'Detect motion', 'Is there a burglar', 'What is happening'

Classify the following input: '{text}'
Classification: 
'''
    
    completion = openai.Completion.create(
            engine='text-davinci-003',
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=prompt)
    
    print(prompt, completion)
    
    try:
        label = Labels(completion.choices[0].text.lower())
        score = 1.0
    except: 
        label = Labels.HELP
        score = 0.0

    return label, score