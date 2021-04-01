from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
import concurrent.futures 
from datetime import datetime as dt
from datetime import timedelta as delta
import pandas as pd

def load_saved_urls(filename):

    try:
        with open(filename, "r") as f:
            saved_urls = json.load(f)

        return saved_urls
    
    except :
        return {}


# load saved data
boats_dict = load_saved_urls("saved_urls.json")




entry_list = [boats_dict[f] for f in list(boats_dict.keys())]

pd.DataFrame(entry_list).to_csv(dt.now().strftime("%Y%m%d_%H%M%S_results.csv"), sep=";", decimal=",")

exit()


with open(dt.now().strftime("%Y%m%d_%H%M%S_results.csv"), "w") as f:

    entry = list(boats_dict.keys())

    columns_names = boats_dict[entry[0]]

    f.write(";".join(columns_names))