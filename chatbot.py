from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from labels import Labels
from classifier_gpt import predict
import os
import logging
import traceback
import numpy as np

logging.basicConfig(level=logging.INFO)

# load Envvariables
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
CONFIG = json.loads(os.getenv('CONFIG'))
logging.info(CONFIG)
ETHEREUM_URL = os.getenv('ETHEREUM_URL')
TEMPERATURE_URL = os.getenv('TEMPERATURE_URL')
CAMERA_URL = os.getenv('CAMERA_URL')

WORDS = {
    Labels.CAMERA: ['camera', 'security', 'burglar'],
    Labels.TEMPERATURE: ['temperature', 'weather', 'rain'],
    Labels.ETHEREUM: ['ethereum', 'money', 'rich'],
    Labels.HELP: ['help']
}
 
def simple_predict(text):
    cleaned_text = text.lower().strip()
    for (clazz, words) in WORDS.items():
        logging.info(clazz)
        logging.info(words)
        if np.any([ word in cleaned_text for word in words ]):
            return clazz, True
    return None, False

# handle ETHEREUM
w3 = Web3(Web3.HTTPProvider(ETHEREUM_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def get_balance(address):
    return w3.fromWei(w3.eth.get_balance(address), 'ether')

def handle_ethereum(address):
    return f'Your current Ethereum balance is {get_balance(address)}'

# handle TEMPERATURE
def load_temperature(login_data, sensor_id):
    login_url = TEMPERATURE_URL + '/api/v1/login'
    result = requests.post(login_url, json=login_data)
    
    if result.status_code != 200:
        return 'Could not fetch the temperature'
    
    token = json.loads(result.text)['token']
    
    url = TEMPERATURE_URL + '/api/v1/graphql'
    headers = {'Authorization': 'Bearer ' + token}

    limit = (datetime.utcnow() - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")

    query = '''query($sensorId: ID!, $limit: DateTime) {
    values(sensorId: $sensorId, limit: $limit) {
      type
      timestamp
      value
    }
  }
'''
    variables = { 'sensorId': sensor_id, 'limit': limit }

    result = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if result.status_code != 200:
        return 'Could not fetch the temperature'
    
    data = json.loads(result.text)
    temperature = data['data']['values'][0]['value']

    return f'Temperature: {temperature}°C'

# handle HELP
def handle_help():
    return '''
This chat bot can handle:
1. requests for the temperature
2. requests for the current view of the appartment
3. requests for the Ethereum funds
4. provide help (this message)
    '''

def handle_temperature(login_data, sensor_id):
    return load_temperature(login_data, sensor_id)

def handle_camera(message, loginData):
    session = requests.Session()
    session.auth = (loginData['username'], loginData['password'])

    response = session.get(CAMERA_URL)
    if response.status_code == 200:
        message.reply_photo(response.content)
        return 'Camera Image'
    else:
        return 'Error while fetching the webcam image'

def handle_request(label, message, config):
    if label == Labels.HELP:
        return handle_help()
    elif label == Labels.ETHEREUM:
        return handle_ethereum(config['address'])
    elif label == Labels.TEMPERATURE:
        return handle_temperature(config['loginData'], config['sensorId'])
    elif label == Labels.CAMERA:
        return handle_camera(message, config['cameraLoginData'])
    else:
        return 'I do not understand'

def start(update: Update, context: CallbackContext):
    logging.info(f'Id {update.effective_chat.id}')
    update.message.reply_text('I\'m your personal bot, please talk to me!')

def help(update: Update, context: CallbackContext):
    update.message.reply_text(handle_help())

def handle_message(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) != CHAT_ID:
        update.message.reply_text('No permissions to talk to this bot')
        return
    try:
        label, found = simple_predict(update.message.text)
        logging.info(f'{label}, {found}')
        
        if not found:
            label, score = predict(update.message.text)
            logging.info(f'{label}, {score}, {update.message.text}')
        
        response = handle_request(label, update.message, CONFIG)
        
        update.message.reply_text(response)
    except Exception as e:
        update.message.reply_text('An internal error has occurred, please try again')
        logging.error(e)
        traceback.print_exc()

def init():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    message_handler = MessageHandler(Filters.text & (~Filters.command), handle_message)
    dispatcher.add_handler(message_handler)
    
    return updater

if __name__ == '__main__':
    updater = init()
    try:
        updater.start_polling()
        logging.info('Started TelegramBot')
        updater.idle()
    except:
        logging.info('Stopping TelegramBot')
        updater.stop()
