from bs4 import BeautifulSoup
import requests
import yaml
import json
import time

CONFIG_FILE = "conf.yml"
DATA_FILE = "data.txt"
NOTIFICATION = "Buy: ${:04.2f} Sell: ${:04.2f} - Percentage: {:03.1f}% {}"

def poll_prices():
    'Gets prices from DolayHoy and reads data from files, then uses decision logic based on % threshold to notify.'

    r = requests.get('http://dolarhoy.bullmarketbrokers.com/')
    soup = BeautifulSoup(r.content, 'html.parser')
    soup_b = soup.find("h4")
    soup_s = soup_b.findNext("h4")
    buy = get_num(soup_b.getText())
    sell = get_num(soup_s.getText())

    config = read_conf()
    web_hook = config['slack']['webhook']
    channel = config['slack']['channel']
    threshold = float(config['dollar']['threshold'])
    last_price = float(read_data())

    difference = sell - last_price
    percentage = (difference / last_price) * 100.
    if percentage > threshold:
        status = "Up"
        notification = NOTIFICATION.format(buy, sell, percentage, status)
        post_to_slack(notification, web_hook, channel)
        save_last_price(sell)
    elif percentage < -threshold:
        status = "Down"
        notification = NOTIFICATION.format(buy, sell, percentage, status)
        post_to_slack(notification, web_hook, channel)
        save_last_price(sell)

def get_num(s):
    'Returns a float from a given string -- works if there is only 1 dot in the string.'
    return float(''.join(char for char in s if char.isdigit() or char == '.'))

def save_last_price(sell):
    'Saves last_price on the file\'s first line.'
    with open(DATA_FILE, "w") as f:
        f.write(str(sell))

def read_conf():
    'Reads yaml configuration file and returns config dictionary.'
    with open(CONFIG_FILE, "r") as yml:
        config = yaml.load(yml)
    return config

def read_data():
    'Reads data file with last saved sell price.'
    with open(DATA_FILE, "r") as f:
        data = f.readline()
    return data

def post_to_slack(text, webhook, channel):
    'Posts a text to Slack via WebHook.'
    jason = {"text": text, "channel": channel}
    requests.post(webhook, data=json.dumps(jason))

while True:
    # executes poll prices every 30 minutes'
    poll_prices()
    time.sleep(1800)