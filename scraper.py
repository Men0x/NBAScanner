import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time
import sys
import chromedriver_binary
import re
from colorama import Fore, Back, Style, init
from termcolor import colored, cprint
from datetime import date, datetime
import os
import webbrowser
#import discord
#from dotenv import load_dotenv

def returnmove(a):
    if "3 Pointer" in a: return "3 Pointer"
    if "Dunk" in a: return "Dunk"
    if "Jump Shot" in a: return "Jump Shot"
    if "Block" in a: return "Block"
    if "Assist" in a: return "Assist"
    if "Layup" in a: return "Layup"
    if "Steal" in a: return "Steal"
    if "Handles" in a: return "Handles"

def returnset(a):
    #LEGENDARY
    if "2020 NBA Finals" in a: return "2020 NBA Finals"
    if "Cosmic" in a: return "Cosmic"
    if "Deck the Hoops" in a: return "Deck the Hoops"
    if "From the Top" in a: return "From the Top"
    if "Holo MMXX" in a: return "Holo MMXX"
    if "Lace 'Em Up" in a: return "Lace 'Em Up"

    #RARE
    if "Conference Semifinals" in a: return "Conference Semifinals"
    if "Denied!" in a: return "Denied!"
    if "Eastern Conference Finals" in a: return "Eastern Conference Finals"
    if "First Round" in a: return "First Round"
    if "Metallic Gold LE" in a: return "Metallic Gold LE"
    if "MVP Moves" in a: return "MVP Moves"
    if "Rookie Debut" in a: return "Rookie Debut"
    if "Run It Back" in a: return "Run It Back"
    if "Season Tip-off" in a: return "Season Tip-off"
    if "So Fresh" in a: return "So Fresh"
    if "The Finals" in a: return "The Finals"
    if "Throwdowns" in a: return "Throwdowns"
    if "Western Conference Finals" in a: return "Western Conference Finals"
    if "With the Strip" in a: return "With the Strip"
    
    #COMMON
    if "Base Set" in a: return "Base Set"
    if "Cool Cats" in a: return "Cool Cats"
    if "Early Adopters" in a: return "Early Adopters"
    if "Got Game" in a: return "Got Game"
    if "Hometown Showdown: Cali vs. NY" in a: return "Hometown Showdown: Cali vs. NY"

def returnserie(a):
    if "Series 1" in a: return 1
    if "Series 2" in a: return 2

def listintodf(soup):

    listings = pd.DataFrame(columns=['player', 'lowest', 'var', 'move', 'set', 'serie', 'links'])

    l = soup.find_all("a", {"href": re.compile("^/listings/")})

    links = []
    for a in soup.find_all('a', href=True):
        if '/listings/' in a['href']: 
            links.append('https://www.nbatopshot.com' + str(a['href']))

    i = 0

    for i in range(len(l)):

        #GET HTML LINE WITH NAME OF PLAYERS, PRICES, AND OTHER FEATURES
        name = BeautifulSoup(str(l[i]), "html.parser").find("h3", {"class": re.compile("^Title__StyledTitle")})
        price = BeautifulSoup(str(l[i]), "html.parser").find("div", {"class": re.compile("^Price__PriceWrapper")})
        full = BeautifulSoup(str(l[i]), "html.parser").find("p", {"class": re.compile("^Description__StyledDescription")})

        #GET TEXT
        name = name.text
        price = int(str(price.text)[5:len(str(price.text))-3])
        full = full.text

        #PARSE THE 'full' STRING
        move = returnmove(full)
        theset = returnset(full)
        serie = returnserie(full)

        #CREATE NEW ROW AND APPEND IT
        new_row = pd.DataFrame([[name, price, 0, move, theset, serie, links[i]]], columns=['player', 'lowest', 'var', 'move', 'set', 'serie', 'links'])
        listings = listings.append(new_row)
    
    #SORT VALUES BY LOWEST PRICE AND RESET INDEXES
    listings = listings.sort_values(by=['lowest'])
    listings = listings.reset_index(drop=True)

    return listings

def printlisting(listings, perc, pdrop):

    listingsarr = []
    head = []
    head.insert(0, {'player': 'Player', 'lowest': 'Lowest', 'var': 'Var', 'move':'Move', 'set': 'Set', 'serie': 'Serie'})

    df = listings
    listings = pd.concat([pd.DataFrame(head), listings], ignore_index=True)

    #CUSTOM PRINTER
    count = 0
    for i in range(len(listings)):
        row = str()
        count2 = 0
        for u in listings:
            if u == 'var' and i != 0:
                if listings.iloc[count][u] > 0:
                    cell = '+' + str(round(listings.iloc[count][u], 2)) + '%'
                else:
                    cell = str(round(listings.iloc[count][u], 2)) + '%'
            else:
                cell = str(listings.iloc[count][u])

            if count2 == 0: space = 12 #Player
            if count2 == 1: space = 8 #Lowest price
            if count2 == 2: space = 8 #Variation
            if count2 == 3: space = 9 #Move
            if count2 == 4: space = 12 #Set
            if count2 == 5: space = 8 #Serie

            if len(cell) >= space:
                cell = cell[0:space-3] + '..'
            
            while len(cell) <= space:
                cell= cell + ' '
            count2 += 1
            row = row + cell
        
        listingsarr.append(row)
        count += 1
    
    count = 0

    #COLOR PICKER (DEPENDIND ON % VARIATION)
    print('____________________________________________________________________')
    for i in listingsarr:
        if count == 0:
            cprint('    ' + listingsarr[count] + ' |', 'cyan', 'on_magenta')
            cprint('____________________________________________________________________|', 'white', 'on_magenta')
            print('                                                                    |')
        else:
            if df['var'][count-1] == 0: color = 'white'
            if df['var'][count-1] > 0: color = 'red'
            if df['var'][count-1] < 0: color = 'green'
            cprint('    ' + listingsarr[count] + ' |', color)
        count += 1
    print('____________________________________________________________________|')

    print('\n\n')

def listbuffer(listings, buffer):

    for i in range(len(listings)):
                for u in range(len(buffer)):
                    count = 0
                    for x in listings.drop(columns=['lowest', 'var']):
                        if listings.drop(columns=['lowest', 'var']).at[i, x] == buffer.drop(columns=['lowest', 'var']).at[u, x]: count += 1
                    if count == len(listings.drop(columns=['lowest', 'var']).columns):
                        listings.at[i, 'var'] = ((listings.at[i, 'lowest'] / buffer.at[u, 'lowest']) - 1)*100
    
    return listings

def alerts(listings, alertlinks, perc, pdrop):

    for i in range(len(listings)):
        if listings['var'][i] <= -perc or listings['lowest'][i] <= pdrop:
            count = 0
            newalert = pd.DataFrame([[listings.at[i, 'player'], listings.at[i, 'links'], 7, listings.at[i, 'lowest'], 0]], columns = ['player', 'links', 'count', 'price', 'time'])
            if alertlinks.empty == True:
                alertlinks = pd.concat([alertlinks, newalert]).reset_index(drop=True)
            else:
                alertlinks = alertlinks.reset_index(drop=True)
                for u in range(len(alertlinks)):
                    if str(newalert['links'][0]) != str(alertlinks['links'][u]):
                        count += 1
                    if count == len(alertlinks):
                        alertlinks = pd.concat([alertlinks, newalert]).reset_index(drop=True)
                
    for i in range(len(alertlinks)):
        if alertlinks['count'][i] == 7:
            now = datetime.now()
            now = str(now.strftime("%H:%M:%S"))
            alertlinks.at[i, 'time'] = now
            webbrowser.open(str(alertlinks['links'][i]))
        
        alertlinks.at[i, 'count'] = alertlinks['count'][i] - 1
        if alertlinks['count'][i] == 0:
            alertlinks = alertlinks.drop(index = i)
    
    if alertlinks.empty == False:
        print('____________________________________________________________________')
        cprint('    Alerts                                                          |', 'cyan', 'on_magenta')
        cprint('____________________________________________________________________|', 'white', 'on_magenta')
        print('                                                                    |')
        for i in range(len(alertlinks)):
            line = '   ' + alertlinks['time'][i] + ' - ' +str(alertlinks['player'][i]) + ' : $' + str(alertlinks['price'][i])
            print(line + (68-len(line))*' ' + '|')
        print('____________________________________________________________________|')
    
    return listings, alertlinks



def main():


    init()

    chrome_driver_path = 'C:/Users/33679/TopShot_scraper/chromedriver.exe'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
    driver.set_page_load_timeout(120)

    print('\n\n\n')

    cprint('    ___________________________________________ ', 'blue')
    cprint('   |              _   ______  ___              |', 'blue')
    cprint('   |             / | / / __ )/   |             |', 'blue')
    cprint('   |            /  |/ / __  / /| |             |', 'cyan')
    cprint('   |    _____  / /|  / /_/ / ___ |             |', 'cyan')
    cprint('   |   / ___/_/_/_|_/_____/_/ _|_|  ___  _____ |', 'cyan')
    cprint('   |   \__ \/ ___/ __ `/ __ \/ __ \/ _ \/ ___/ |', 'cyan')
    cprint('   |  ___/ / /__/ /_/ / / / / / / /  __/ /     |', 'cyan')
    cprint('   | /____/\___/\__,_/_/ /_/_/ /_/\___/_/      |', 'magenta')
    cprint('   |                                           |', 'magenta')
    cprint('   |___________________________________________|', 'magenta')

    print('\n\n\n')
    
    choice = 'n'
    while(choice=='n'):

        cprint('  Enter a valid NBA TopShot search URL :  \n', 'cyan', 'on_magenta')
        url = input()

        driver.get(url)
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 20000)")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        listings = listintodf(soup)

        print('\n')

        printlisting(listings.drop(columns=['links']), 100, 0)

        f = False
        while(f == False):  

            cprint('  Are these moments you want to track? (y/n)  \n', 'cyan', 'on_magenta')
            choice = input()

            print('\n')

            if choice != 'y' and choice != 'n':
                cprint('  Please input a valid answer  \n', 'cyan', 'on_magenta',)
            else:
                f = True
    
    perc = -1
    while perc <= 0 or perc >= 100:
        cprint('  Insert % of price drops you want to be notified at :  \n', 'cyan', 'on_magenta')
        perc = float(input())

        print('\n')

        if perc <= 0 or perc >= 100:
            cprint('  Please input a valid answer  \n', 'cyan', 'on_magenta')

    print('\n')

    cprint('  Insert price cap you want to be notified at :  \n', 'cyan', 'on_magenta')
    pdrop = int(input())

    print('\n')

    cprint('  Insert session name :  \n', 'cyan', 'on_magenta')
    sessname = str(input())

    print('\n\n\n')


    if listings.empty == False: buffer = listings
    alertlinks = pd.DataFrame(columns = ['player', 'links', 'count', 'price', 'time'])
    n = 0
    while n == 0:

        driver.get(url)
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 20000)")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        #TURN DATA INTO DATAFRAME
        listings = listintodf(soup)

        #BUFFER
        if (listings.empty == False) and ('buffer' in locals()):

            listings = listbuffer(listings, buffer)
            buffer = listings


        cprint('     _   ______  ___          ___' + len(sessname)*'_' + '___', 'blue')
        cprint('    / | / / __ )/   |        |   ' + len(sessname)*' ' + '   |', 'cyan')
        cprint('   /  |/ / __  / /| |        |   ' + sessname + '   |', 'cyan')
        cprint('  / /|  / /_/ / ___ |        |___' + len(sessname)*'_' + '___|', 'cyan')
        cprint(' /_/_|_/_____/_/  |_|    ', 'magenta')

        today = date.today()
        now = datetime.now()
        today = str(today.strftime("%B %d, %Y"))
        now = str(now.strftime("%H:%M:%S"))

        cprint('\n\n    ' + now + '                       ' + today, 'cyan')
        cprint('\n    Price notification : $' + str(pdrop),'cyan')
        cprint('\n    % drop notification : +' + str(perc) + '%','cyan')

        #ALERT
        listings, alertlinks = alerts(listings, alertlinks, perc, pdrop)
        
        print('\n')

        #PRINT
        printlisting(listings.drop(columns=['links']), perc, pdrop)

        time.sleep(2)
        #driver.refresh()


if __name__ == "__main__":

    main()
