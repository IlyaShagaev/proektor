import paho.mqtt.client as mqtt
import settings
import telebot
import requests
import json
from telebot import types

def on_connect(client, userdata, flags, rc):
    client.subscribe("ilya/shagaev/#")

def on_message(client, userdata, msg):
    print(msg.payload.decode("utf-8", "ignore"))

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(settings.MQTT_SERVER, settings.MQTT_PORT, 60)

client.loop_start()

bot = telebot.TeleBot(settings.BOT_TOKEN)
user_dict = {}

def driver_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("ZOOM"), types.KeyboardButton("LMS.MAI"))
    return markup

def conference_stop_button():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Остановить конференцию"))
    return markup

class ZOOM:

    def __init__(self, name):
        self.driver = name
        self.aud = None
        self.id = None
        self.password = None

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,'Добро пожаловать!')


@bot.message_handler(commands=['help'])
def help_info(message):
    bot.send_message(message.chat.id,"/start - Приветсвие\n/help - Список команд\n/work - Начать конференцию")

@bot.message_handler(commands=['work'])
def welcome(message):
    url = "http://" + settings.REST_SERVER + ":" + settings.REST_PORT + "/users_list/" + str(message.chat.id)
    statement = requests.get(url).text
    if statement == 'True':
        msg = bot.send_message(message.chat.id, 'Выберите платформу:', reply_markup=driver_keyboard())
        bot.register_next_step_handler(msg, platform_choice_step)
    elif statement == 'False':
        bot.send_message(message.chat.id,'У вас нет доступа.')

def platform_choice_step(message):
    if message.text == 'ZOOM':
        chat_id = message.chat.id
        driver = message.text
        mqttCommand = ZOOM(driver)
        user_dict[chat_id] = mqttCommand
        msg = bot.send_message(message.chat.id, 'Номер аудитории: ')
        bot.register_next_step_handler(msg, zoom_aud_step)
    elif message.text == 'LMS.MAI':
        bot.send_message(message.chat.id,'Еще не готово')

def zoom_aud_step(message):
    chat_id = message.chat.id
    aud = message.text
    mqttCommand = user_dict[chat_id]
    mqttCommand.aud = aud
    msg = bot.send_message(message.chat.id, 'ID конференции: ')
    bot.register_next_step_handler(msg, zoom_id_step)

def zoom_id_step(message):
    chat_id = message.chat.id
    id = str(message.text)
    mqttCommand = user_dict[chat_id]
    mqttCommand.id = id
    msg = bot.send_message(message.chat.id, 'Пароль конференции: ')
    bot.register_next_step_handler(msg, zoom_password_step)

def zoom_password_step(message):
    chat_id = message.chat.id
    password = str(message.text)
    mqttCommand = user_dict[chat_id]
    mqttCommand.password = password
    mqtt_msg = '{"id":"' + str(chat_id) + '","driver": "' + str(
        mqttCommand.driver) + '", "command": "ON", "params": {"meeting_id": "' + str(
        mqttCommand.id) + '", "password": "' + str(mqttCommand.password) + '"}} '

    client.publish('univer/' + str(mqttCommand.aud), mqtt_msg)
    msg = bot.send_message(chat_id, 'Конференция начата',reply_markup=conference_stop_button())
    bot.register_next_step_handler(msg, zoom_end_step)

def zoom_end_step(message):

    if message.text == 'Остановить конференцию':
        chat_id = message.chat.id
        mqttCommand = user_dict[chat_id]
        mqtt_msg = '{"id":"' + str(chat_id) + '","driver": "' + str(
            mqttCommand.driver) + '", "command": "OFF", "params": {"meeting_id": "' + str(
            mqttCommand.id) + '", "password": "' + str(mqttCommand.password) + '"}} '
        client.publish('univer/' + str(mqttCommand.aud), mqtt_msg)
        bot.send_message(chat_id, 'Конференция остановлена')

bot.enable_save_next_step_handlers(delay=1)

bot.load_next_step_handlers()

bot.polling()
