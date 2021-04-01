import re
import os
import json

def load_saved_urls(filename):

        with open(filename, "r") as f:
            saved_urls = json.load(f)
        return saved_urls

        

if __name__ == "__main__":


    
    # load saved data
    boats_dict = load_saved_urls("./saved_urls.json")

    for url in boats_dict:

        price_str=boats_dict[url]["Preis"]
        print(price_str)

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
    #print(boats_dict)
        
        match = re.search("EUR\d+\,\d+", price_str)
        if match:
            wahrung = "euro"
            betrag = float(match[0].split("EUR")[1].replace(",", ""))
            print("betrag ", betrag)
            pass


        match = re.search("US\$\d+\,\d+", price_str)
        if match:
            wahrung = "usd"
            betrag = float(match[0].split("US$")[1].replace(",", ""))
            print("betrag ", betrag)
            pass      

        match = re.search("Can\$\d+\,\d+", price_str)
        if match:
            wahrung = "can"
            betrag = float(match[0].split("Can$")[1].replace(",", ""))
            print("betrag ", betrag)
            pass    

        match = re.search("\£\d+\,\d+", price_str)
        if match:
            wahrung = "pfund"
            betrag = float(match[0].split("£")[1].replace(",", ""))
            print("betrag ", betrag)
            pass    




    #