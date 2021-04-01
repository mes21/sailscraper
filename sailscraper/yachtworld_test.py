
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


    try:
        html = requests.get(url, headers=HEADER).text
        #print("page len:", len(html))
        return BeautifulSoup(html, features="lxml")
    
    except requests.exceptions.MissingSchema:
        return None

def load_saved_urls(filename):

    if os.path.isdir(filename):
        with open(filename, "r") as f:
            saved_urls = json.load(f)

        return saved_urls
    
    else:
        return {}

def save_urls(filename, url_list):

    with open(filename, "w") as f:
        json.dump(url_list, f, indent=4, ensure_ascii=True)


def price_str_analyse(price_str):

    wahrung = ""
    betrag = 0.0
    versteuert = ""
    reserviert = ""

    match = re.search("EUR\d+\,\d+", price_str)
    if match:
        wahrung = "euro"
        betrag = float(match[0].split("EUR")[1].replace(",", ""))
        #print(" ", match)
        pass

    else:
        match = re.search("US\$\d+\,\d+", price_str)
        if match:
            wahrung = "usd"
            betrag = float(match[0].split("US$")[1].replace(",", ""))
            #print(" ", match)
            pass      
        else:
            match = re.search("Can\$\d+\,\d+", price_str)
            if match:
                wahrung = "can"
                betrag = float(match[0].split("can$")[1].replace(",", ""))
                #print(" ", match)
                pass    
            else:
                match = re.search("\£\d+\,\d+", price_str)
                if match:
                    wahrung = "pfund"
                    betrag = float(match[0].split("£")[1].replace(",", ""))
                    #print(" ", match)
                    pass    

    match = re.search("Nicht versteuert", price_str)
    if match:
        versteuert = "Nein"
    else:
        match = re.search("Versteuert", price_str)
        if match:
            versteuert = "Ja"

    match = re.search("Reserviert", price_str)
    if match:
        reserviert = "Ja"
    else:
        reserviert = "Nein"

    return betrag, wahrung, versteuert, reserviert


def get_boat_details(url):
    time.sleep(1)
    ret_dict = {"url":url}
    soup = get_soup(url)
    
    if soup:
        
        try:
            # extract information from boat page
            fc = soup.find("div", {"class":"firstColumn"}).text
            try:
                ret_dict["Jahr"] = int(fc.split("Jahr:")[1].split("Länge")[0])
            except:
                ret_dict["Jahr"] = None
            
            try:
                ret_dict["Laenge"] = int(fc.split("Länge:")[1].split("mMotor-/Treibstoffart")[0])
            except:
                ret_dict["Laenge"] = None

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
                ret_dict["Preis_String"] = tc.split("aktueller Preis:")[1].rstrip().replace("\xa0", "")
            except:
                ret_dict["Preis_String"] = None

            # re price and make integer 
            if ret_dict["Preis_String"]:
                ret_dict["Preis"], ret_dict["Waehrung"], ret_dict["Versteuert"], ret_dict["Reserviert"] = price_str_analyse(ret_dict["Preis_String"])
            else:
                ret_dict["Preis"], ret_dict["Waehrung"], ret_dict["Versteuert"], ret_dict["Reserviert"] = None, None, None, None
            

            return ret_dict
        
        except:
            return None

    return None

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

if __name__ == "__main__":

    # load base url
    soup = get_soup(BASE_URL_NO_FILTER)
    # find boat entrys 
    results = soup.find("div", { "id" : "searchResultsCount" }).text
    try:
        res_count = int(results.split("\n")[-2].replace(".", ""))
    except:
        res_count = 0
    print("gefundene Boote:", res_count)


    # load saved data
    boats_dict = load_saved_urls("saved_urls.json")
    
    boats_list = boats_dict.keys()
    
    new_boats_list = []
    count = 0



    while True:
        
        printProgressBar(count, res_count, prefix = 'Progress:', suffix = 'Complete', length = 50)

        # add urls of boats to list
        boats_on_page = []
        boats_on_page.extend(soup.find_all("div", {"class":"listing row"}))
        boats_on_page.extend(soup.find_all("div", {"class":"listing premier row"}))
        
        #print("on page:", len(boats_on_page))
        link_list = [f.find("a")["href"] for f in boats_on_page]
        link_list = [f for f in link_list if "https://www." in f]

        # load multiple pages 
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(get_boat_details, link_list)     
            # check single results
            boats_list = boats_dict.keys()
            for result in results:
                count += 1
                if result:
                    # check if entry exists in the "boats_dict"
                    if result["url"] in boats_list:
                        # old entry
                        # check for age of entry
                        boats_dict[result["url"]]["Datum_Letztes_Update"] = dt.now().strftime("%Y-%m-%d")
                        boats_dict[result["url"]]["Alter_Anzeige"] = (boats_dict[result["url"]]["Datum_Letztes_Update"] - boats_dict[result["url"]]["Datum_Ersterfassung"]).days
                        # check for price updates
                        if boats_dict[result["url"]]["Preis"] != result["Preis"]:
                            # price update detected
                            # update price
                            boats_dict[result["url"]]["Preis"] = result["Preis"]
                            # inc "Preis_Updates"
                            boats_dict[result["url"]]["Preis_Updates"] += 1
                            boats_dict[result["url"]]["Preis_Entwicklung"] += (str(result["Preis"]) + ",")
                            boats_dict[result["url"]]["Preis_Ent_Datum"] += boats_dict[result["url"]]["Datum_Letztes_Update"] + ","
                                                                                

                    else:
                        # new entry
                        boats_dict[result["url"]] = result
                        boats_dict[result["url"]]["Preis_Updates"] = 0
                        boats_dict[result["url"]]["Preis_Entwicklung"] = str(result["Preis"]) + ","
                        boats_dict[result["url"]]["Preis_Ent_Datum"] = None
                        # add date of entry
                        boats_dict[result["url"]]["Datum_Ersterfassung"] = dt.now().strftime("%Y-%m-%d")
                        boats_dict[result["url"]]["Datum_Letztes_Update"] = None
                        boats_dict[result["url"]]["Alter_Anzeige"] = None


            
        
        '''
        for link in 
            if link not in boats_list:
                
                details = get_boat_details(link)
                if details is not None:
                    boats_dict[link] = details
                    new_boats_list.append(link)

        '''

        
        # get next page
        next_page = soup.find_all("a", {"class":"navNext"})
        next_page = next_page[-1]["href"]

        #print(next_page)

        
        last_page = soup.find("a", {"class":"navLast"})["href"]
        # save new data
        save_urls("saved_urls.json", boats_dict)

        # check if next page is new
        if next_page != last_page:
            soup = get_soup("https://www.yachtworld.de" + next_page)
            
            #print("on list:", len(new_boats_list))
        else:
            break

    print("Erstelle .csv")

    entry_list = [boats_dict[f] for f in list(boats_dict.keys())]
    pd.DataFrame(entry_list).to_csv(dt.now().strftime("%Y%m%d_%H%M%S_results.csv"), sep=";", decimal=",")
    
    print("Ende")
        
        