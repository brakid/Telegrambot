# Telegram Chatbot

The messenger service [Telegram](https://telegram.org/) allows users to set up their own chatbots to interact with. This project aims to create a basic, [Machine Learning](https://en.wikipedia.org/wiki/Machine_learning) powered bot that understands the intent of a user request and triggers an action based on the intent.

```
*Question:* 'what is the current temperature' -> *Classification:* Temperature Request -> *Action:* fetch the current temperature
```

Training the classifier is a [supervised, multi-class task](https://monkeylearn.com/blog/intent-classification/), as we have several intents but want to find a single one for the request sent by the users.
In the first version we used the [fasttext](https://fasttext.cc/) library to train the classifier used in the project. Fasttext represents words by looking at character-level n-grams. That way it can address out of vocabulary words. By default fasttext looks at each words individually to classify a sentence. This approach has a hard time to figure our semantic similarities between completely different words. Especially when having little training data these semantic relationships hardly are captured. This leads to cases where the chatbot cannot make sense of sentences such as *'do I need gloves'* when not having seen the words in training.

The address the semantic similarity between words, in version 2, we have switched to use a [BERT Transformer](https://arxiv.org/abs/1810.04805) to embed sentences into a single vector. BERT is a large-scale language model, that has been trained to capture semantic similarities (e.g via a [masked language model task](https://www.projectpro.io/recipes/what-is-masked-language-modeling-transformers)). As the original BERT model is quite large (110m parameters) and GPU memory on the [NVIDIA Jetson Nano 2GB](https://developer.nvidia.com/embedded/jetson-nano-2gb-developer-kit) is limited to 2GB, we are using a minified version of BERT called [DistilBERT](https://arxiv.org/abs/1910.01108). Compared to BERT, DistilBERT is 40% smaller while retaining 97% of the model performance.

As BERT is 'just' embedding a sentence into a semantically rich vector, we need to add a classifier that predicts the intent for a given embedded sentence. We use a standard Multi-level perceptron for that case with 2 layers (inout & output).

The main advantage of using BERT to embed requests is that the chatbot now is able to process requests such as *'do i need gloves'* and correctly predict the intent to be temperature-based even when not having seen the term gloves in the training data. As the language model training part used a large text corpus, it is able to capture the semantics in the embedding, removing this task from the  classifier. This ideally allows us to achieve a better performance on unseed sentences or synonyms for the intent classification.

Training the BERT-based intent classifier: [BERT Classifier.ipynb](https://github.com/brakid/MLNotebooks/blob/master/MLBot/BERT%20Classifier.ipynb)

In total the bot currently supports 3 intents:
1. explaining itself (*HELP*)
2. fetching the temperature in my appartement using the [GraphQL API](https://graphql.org/) exposed by the [Sensor project](https://github.com/brakid/Sensor) I implemented a while ago (*TEMPERATURE*)
3. fetch my current balance of [Ethereum](https://ethereum.org/en/) via the [web3](https://web3py.readthedocs.io/en/stable/) Python library(*ETHEREUM*)

Each of the 3 intents has a different handler that generates the response for the chatbot. At the moment the interactions are quite limited, as the chatbot does not include slotfilling or can keep a conversation over multiple turns.