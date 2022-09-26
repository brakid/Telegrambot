# Telegram Chatbot

The messenger service [Telegram](https://telegram.org/) allows users to set up their own chatbots to interact with. This project aims to create a basic, [Machine Learning](https://en.wikipedia.org/wiki/Machine_learning) powered bot that understands the intent of a user request and triggers an action based on the intent.

```
*Question:* 'what is the current temperature' -> *Classification:* Temperature Request -> *Action:* fetch the current temperature
```

Training the classifier is a [supervised, multi-class task](https://monkeylearn.com/blog/intent-classification/), as we have several intents but want to find a single one for the request sent by the users.
We use the [fasttext](https://fasttext.cc/) library to train the classifier used in the project.

In total the bot currently supports 3 intents:
1. explaining itself (*HELP*)
2. fetching the temperature in my appartement using the [GraphQL API](https://graphql.org/) exposed by the [Sensor project](https://github.com/brakid/Sensor) I implemented a while ago (*TEMPERATURE*)
3. fetch my current balance of [Ethereum](https://ethereum.org/en/) via the [web3](https://web3py.readthedocs.io/en/stable/) Python library(*ETHEREUM*)

Each of the 3 intents has a different handler that generates the response for the chatbot. At the moment the interactions are quite limited, as the chatbot does not include slotfilling or can keep a conversation over multiple turns.