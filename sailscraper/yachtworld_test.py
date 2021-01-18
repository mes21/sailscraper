
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


HEADER = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referrer': 'https://google.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache',
        }      

BASE_URL = "https://www.yachtworld.de/core/listing/cache/searchResults.jsp?cit=true&slim=quick&ybw=&sm=3&searchtype=homepage&Ntk=boatsDE&Ntt=&is=false&man=&hmid=0&ftid=0&enid=0&type=%28Sail%29&fromLength=10&toLength=14&fromYear=2000&toYear=2002&luom=127&currencyid=1004&city=&pbsint=&boatsAddedSelected=-1#&No=0&ps=50"


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

    html = requests.get(BASE_URL, headers=HEADER).text
    return BeautifulSoup(html, features="lxml")

if __name__ == "__main__":
    
    
    #url = build_serch_url(fromLength=10,toLength=14,fromYear=1950,toYear=2020)
    #print(url)
    soup = get_soup(BASE_URL)
    
    results = soup.find("div", { "id" : "searchResultsCount" }).text
    print(results)
    
    list_of_boats = []

    list_of_boats.extend(soup.find_all("div", { "class" : "listing row" }))
    
    print("number of entry:", len(list_of_boats))

    links_list = []
    links_list.extend([f.find("a")["href"] for f in list_of_boats])

    print("links:", links_list)