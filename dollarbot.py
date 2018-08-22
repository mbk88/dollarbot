from bs4 import BeautifulSoup
import requests
import json
import time
config_file = "conf.yml"

def poller():
    r = requests.get('http://dolarhoy.bullmarketbrokers.com/')
    soup = BeautifulSoup(r.content, 'html.parser')
    soup_b = soup.find("h4")
    soup_s = soup_b.findNext("h4")
    buy = get_num(soup_b.getText())
    sell = get_num(soup_s.getText())

    config = read_conf()
    last_price = float(config[0])
    threshold = float(config[1])
    difference = sell - last_price
    percentage = (difference / last_price) * 100.
    if percentage > threshold:
        post(buy, sell, "Up", percentage)
        save_last_price(sell)
    elif percentage < -threshold:
        post(buy, sell, "Down", percentage)
        save_last_price(sell)

# returns a float from a given string -- works if there's only 1 dot in the string
def get_num(s):
    return float(''.join(char for char in s if char.isdigit() or char == '.'))

# saves last_price on the file's first line -- TODO fix issues with newlines
def save_last_price(sell):
    data = read_conf()
    data[0] = str(sell)
    with open(config_file, "w") as f:
        for s in data:
            f.write(s+'\n')

# reads yaml configuration file and returns list with values
def read_conf():
    with open(config_file, "r") as f:
        data = f.readlines()
        # first line of the list would be last_price, second line would be percentage threshold
    return data

# posts dollar's buy and sell prices with % difference to Slack
def post(buy, sell, status, perc):
    jason = {}
    jason["text"] = "Buy: ${} Sell: ${} - Percentage: {:04.2f}% {}".format(buy, sell, perc, status)
    url = "https://hooks.slack.com/services/"
    r = requests.post(url, data=json.dumps(jason))


while True:
    poller()
    time.sleep(900)

