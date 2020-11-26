import paho.mqtt.client as mqtt
import settings
import json
import cv2
import pyautogui
import time

def enter_the_conference(login,password):
    pyautogui.press('win', interval=0.5)
    time.sleep(3)
    pyautogui.write('zoom')
    time.sleep(3)
    pyautogui.press('enter', interval=0.5)
    time.sleep(3)

    x, y = pyautogui.locateCenterOnScreen('plus.png', confidence=0.9)
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(2)

    pyautogui.write(login, interval=0.5)
    x, y = pyautogui.locateCenterOnScreen('Enter.png', confidence=0.7)
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(5)

    pyautogui.write(password, interval=0.5)
    x, y = pyautogui.locateCenterOnScreen('EnterAftenPassword.png', confidence=0.9)
    pyautogui.moveTo(x, y)
    pyautogui.click()

    '''time.sleep(60) - Разворачивание экрана на полную (преподу нужно успеть за 60 секунд принять пользователя)
    x, y = pyautogui.locateCenterOnScreen('window.png', confidence=0.9)
    pyautogui.moveTo(x, y)
    pyautogui.click()'''
    print('Скрипт на запуск Выполнен')


def esc_the_conference():
    x, y = pyautogui.locateCenterOnScreen('escape.png',confidence=0.9)
    pyautogui.moveTo(x, y)
    pyautogui.click()

    x, y = pyautogui.locateCenterOnScreen('escape_the_conf.png',confidence=0.9)
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(3)

    x, y = pyautogui.locateCenterOnScreen('escape.png', confidence=0.9)
    pyautogui.moveTo(x, y)
    pyautogui.click()

    print('Скрипт на выключение Выполнен')

def on_connect(client, userdata, flags, rc):
    client.subscribe("univer/555/#")

def on_message(client, userdata, msg):
    print(msg.payload.decode("utf-8", "ignore"))
    message_dictionary = json.loads(msg.payload.decode("utf-8", "ignore"))
    login = str(message_dictionary['params']['meeting_id'])
    password = str(message_dictionary['params']['password'])
    if str(message_dictionary['command']) == 'ON':
        enter_the_conference(login,password)
    elif str(message_dictionary['command'])=='OFF':
        esc_the_conference()


    '''Проверить сообщение -> запуск'''



client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message



client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(settings.MQTT_SERVER, settings.MQTT_PORT, 60)

client.loop_start()

while True:
    pass
