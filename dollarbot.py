from bs4 import BeautifulSoup
import urllib3
import re
import requests
import json
import threading

def dollar_poller():
    dolar_venta = 0
    threading.Timer(900.0, dollar_poller).start()
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://dolarhoy.bullmarketbrokers.com/')
    soup = BeautifulSoup(r.data, 'html.parser')
    soupc = soup.find("h4")
    soupv = soupc.findNext("h4")
    dolar_c = re.search(r'\d\d\.\d\d', str(soupc)).group(0)
    dolar_v = re.search(r'\d\d\.\d\d', str(soupv)).group(0)
    dif = dolar_venta - float(dolar_v)

    if float(dolar_v) > dolar_venta:
        post_dollar_in_slack(dolar_c, dolar_v)
        dolar_venta = dolar_v
    elif dif > 0.10 or dif < -0.10:
        post_dollar_in_slack(dolar_c, dolar_v)
        dolar_venta = dolar_v

def post_dollar_in_slack(compra, venta):
    jason = {}
    jason["text"] = "Compra: "+str(compra)+"  Venta: "+str(venta)
    url = "https://hooks.slack.com/services/"
    r = requests.post(url, data=json.dumps(jason))


dollar_poller()
