import telebot
from selenium import webdriver
import re
import os
import time
import configparser

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def make_screen(message):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    url = message.text
    driver.get(url)
    filename = 'screens/' + str(message.chat.id) + '_' + str(int(round(time.time() * 1000))) +'.png'
    print("Making screen... ", filename)
    s = lambda x: driver.execute_script('return document.body.parentNode.scroll' + x)
    driver.set_window_size(1920, s('Height'))
    driver.find_element_by_tag_name('body').screenshot(filename)
    screen = open(filename, 'rb')
    return screen, filename


config = configparser.ConfigParser()
config.read('config.ini')
token = config['DEFAULT']['token']
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Привет, я бот, который делает скрины веб страниц. Вы можете отправить мне ссылку на нужную страницу')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if re.match(regex, message.text) is not None:
        bot.send_message(message.chat.id, 'Ссылка получена, делаю скрин')
        screen, filename = make_screen(message)
        bot.send_document(message.chat.id, screen)
        bot.send_message(message.chat.id,
                             'Закринить еще что-то?')
        screen.close()
        os.remove(filename)
    else:
        bot.send_message(message.chat.id, 'Ссылка не верна, попробуйте в таком формате: http://www.example.com')


bot.polling()