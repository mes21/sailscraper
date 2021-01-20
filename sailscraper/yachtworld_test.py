
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import json
import os
import time

HEADER = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referrer': 'https://google.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en,de-DE,de;q=0.9',
        'Pragma': 'no-cache',
        }      

BASE_URL_NO_FILTER = "https://www.yachtworld.de/core/listing/cache/searchResults.jsp?slim=quick&sm=3&currencyid=1004&searchtype=homepage&fromPrice=40000&Ntk=boatsDE&luom=127&cit=true&toPrice=70000&type=%28Sail%29&ps=50&No=0"

def build_serch_url(type_="%28Sail%29",
                    fromLength=None,
                    toLength=None,
                    fromYear=None,
                    toYear=None,
                    fromPrice=None,
                    toPrice=None,
                    ):
    # switch to replace
    base = "https://www.yachtworld.de/core/listing/cache/searchResults.jsp?cit=true&slim=quick&ybw=&sm=3&searchtype=homepage&Ntk=boatsDE&Ntt=&is=false&man=&hmid=0&ftid=0&enid=0&type=%28Sail%29&fromLength=10&toLength=14&fromYear=2000&toYear=2002&fromPrice=55000&toPrice=60000&luom=127&currencyid=1004&city=&pbsint=&boatsAddedSelected=-1#?"

    base += "cit=true&slim=quick&ybw=&sm=3&searchtype=homepage&Ntk=boatsDE&Ntt=&is=&man=&hmid=0&ftid=0&enid=0"

    if type_:
        base += f"&type=%28{type_}"
    if fromLength:
        base += f"&fromLength={str(fromLength)}"
    if toLength:
        base += f"&toLength={str(toLength)}"
    if fromYear:
        base += f"&fromYear={str(fromYear)}"
    if toYear:
        base += f"&toYear={str(toYear)}"
    if fromPrice:
        base += f"&fromPrice={str(fromPrice)}"
    if toPrice:
        base += f"&toPrice={str(toPrice)}"

    return base


def get_soup(url):

    html = requests.get(url, headers=HEADER).text
    print("page len:", len(html))
    return BeautifulSoup(html, features="lxml")


def load_saved_urls(filename):

    if os.path.isdir(filename):
        with open(filename, "r") as f:
            saved_urls = json.load(f)

        return saved_urls
    
    else:
        return {}

def save_urls(filename, url_list):

    with open(filename, "w") as f:
        json.dump(url_list, f, indent=4)


def get_boat_details(url):
    time.sleep(1)
    ret_dict = {"url":url}
    soup = get_soup(url)
    print(url)
    
    try:
        fc = soup.find("div", {"class":"firstColumn"}).text
        try:
            ret_dict["Jahr"] = int(fc.split("Jahr:")[1].split("Länge")[0])
        except:
            ret_dict["Jahr"] = None
        
        try:
            ret_dict["Länge"] = int(fc.split("Länge:")[1].split("mMotor-/Treibstoffart")[0])
        except:
            ret_dict["Länge"] = None

        try:
            ret_dict["Motor"] = fc.split("mMotor-/Treibstoffart:")[1].rstrip()
        except:
            ret_dict["Motor"] = None

        sc = soup.find("div", {"class":"secondColumn"}).text
        
        try:
            ret_dict["Liegeplatz"] = sc.split("Liegeplatz:")[1].split("Rumpfmaterial:")[0]
        except:
            ret_dict["Liegeplatz"] = None
        
        try:
            ret_dict["Rumpfmaterial"] = sc.split("Rumpfmaterial:")[1].split("YW#:")[0].rstrip()
        except:
            ret_dict["Rumpfmaterial"] = None

        try:
            ret_dict["YW#"] = sc.split("YW#:")[1].rstrip()
        except:
            ret_dict["YW#"] = None

        tc = soup.find("div", {"class":"thirdColumn"}).text

        try:
            ret_dict["Preis"] = tc.split("aktueller Preis:")[1].rstrip().replace("\xa0", "")
        except:
            ret_dict["Preis"] = None

        print(ret_dict)
        return ret_dict
    
    except:

        return None




if __name__ == "__main__":

    soup = get_soup(BASE_URL_NO_FILTER)
    
    results = soup.find("div", { "id" : "searchResultsCount" }).text
    print(results)
    
    boats_dict = load_saved_urls("saved_urls.json")
    
    boats_list = boats_dict.keys()
    
    new_boats_list = []
    
    while True:
        boats_on_page = []
        boats_on_page.extend(soup.find_all("div", {"class":"listing row"}))
        boats_on_page.extend(soup.find_all("div", {"class":"listing premier row"}))
        
        print("on page:", len(boats_on_page))

        for link in [f.find("a")["href"] for f in boats_on_page]:
            if link not in boats_list:
                
                details = get_boat_details(link)
                if details is not None:
                    boats_dict[link] = details
                    new_boats_list.append(link)



        
        
        next_page = soup.find_all("a", {"class":"navNext"})
        next_page = next_page[-1]["href"]

        print(next_page)

        
        last_page = soup.find("a", {"class":"navLast"})["href"]

        save_urls("saved_urls.json", boats_dict)

        if next_page != last_page:
            soup = get_soup("https://www.yachtworld.de" + next_page)
            
            print("on list:", len(new_boats_list))
        else:
            break

        
        