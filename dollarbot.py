from bs4 import BeautifulSoup
import requests
import json
import time

config_file = "conf.yml"
data_file = "data.txt"

# gets prices from DolayHoy and reads data from files, then uses decision logic based on % threshold to notify
def poll_prices():
    r = requests.get('http://dolarhoy.bullmarketbrokers.com/')
    soup = BeautifulSoup(r.content, 'html.parser')
    soup_b = soup.find("h4")
    soup_s = soup_b.findNext("h4")
    buy = get_num(soup_b.getText())
    sell = get_num(soup_s.getText())

    config = read_conf()
    slack_hook = config[0]
    threshold = float(config[1])
    last_price = float(read_data())
    difference = sell - last_price
    percentage = (difference / last_price) * 100.
    if percentage > threshold:
        notification = "Buy: ${:04.2f} Sell: ${:04.2f} - Percentage: {:04.1f}% Up".format(buy, sell, percentage)
        post_to_slack(notification, slack_hook)
        save_last_price(sell)
    elif percentage < -threshold:
        notification = "Buy: ${:04.2f} Sell: ${:04.2f} - Percentage: {:04.1f}% Down".format(buy, sell, percentage)
        post_to_slack(notification, slack_hook)
        save_last_price(sell)

# returns a float from a given string -- works if there's only 1 dot in the string
def get_num(s):
    return float(''.join(char for char in s if char.isdigit() or char == '.'))

# saves last_price on the file's first line
def save_last_price(sell):
    with open(data_file, "w") as f:
        f.write(str(sell))

# reads yaml configuration file and returns list with values
def read_conf():
    with open(config_file, "r") as f:
        data = f.readlines()
        # first line of the list would be Slack hook, second line would be percentage threshold
    return data

# reads data file with last saved sell price
def read_data():
    with open(data_file, "r") as f:
        data = f.readline()
    return data

# posts a text to Slack
def post_to_slack(text, webhook):
    jason = {"text": text}
    requests.post(webhook, data=json.dumps(jason))

# execute poll prices every 30 minutes
while True:
    poll_prices()
    time.sleep(1800)