import os
import importlib
import re

import pandas as pd
from collections import OrderedDict as odict

from flask import Flask, render_template

FILE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

PICKED_POSTS = pd.read_pickle(os.path.join(FILE_DIR, 'pp.xz'))
PICKED_POSTS = odict(reversed(list(PICKED_POSTS.items())))

for aid, post in PICKED_POSTS.items():
    post.img_urls = get_url_images_in_text(post.content)[:5]

def get_url_images_in_text(text):
    '''finds image urls'''
    urls = []
    results = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg)', text)
    for x in results:
      urls.append(x)
    return urls


@app.route('/')
def index():
    return render_template("index.html", PICKED_POSTS=PICKED_POSTS)

