import datetime

import requests
from bs4 import BeautifulSoup
import random
import urllib.request
import constants

import time
import clickup
import func


def get_meme():
    response = requests.get(constants.meme_url + 'programming')
    soup = BeautifulSoup(response.content, 'lxml')
    divs = soup.find_all('div', class_='item-aux-container')
    imgs = []
    for div in divs:
        img = div.find('img')['src']
        if img.startswith('http') and img.endswith('jpeg'):
            imgs.append(img)
    print(imgs)
    meme = random.choice(imgs)
    urllib.request.urlretrieve(meme, "temp.jpg")

clickup.create_json()
