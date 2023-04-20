#!/usr/bin/env python3

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import re

global DRIVER_LOCATION
DRIVER_LOCATION = "/home/derry/Programming/Backend/Python/note/selenium/chromedriver"

global options
options = Options()
options.add_argument("start-maximized")
options.binary_location = r'/usr/bin/vivaldi-stable'


def get_link(a):
    try:
        link = driver.find_element(By.XPATH, a).get_attribute('href')
        print(link)
        return link
    except:
        return False


def get_links(link, page):
    driver.get(link)

    i = 0
    while i < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i = i + 1

    driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
    time.sleep(0.3)


    links = []
    links.append(f"page:{page}")
    for i in range(1, 100):
        target1 = '/html/body/div[1]/div/div[1]/div/main/div[2]/div[5]/div[1]/div[{}]/div/div/a'.format(i)
        target2 = '/html/body/div[1]/div/div[1]/div/main/div[2]/div[5]/div[1]/div[{}]/div[2]/div/a'.format(i)

        link_a = get_link(target1)
        link_b = get_link(target2)

        if link_a or link_b:
            # a not none
            if link_a:
                links.append(link_a)
                continue
            else:
                links.append(link_b)

    return links


def scrape_page_typeA(page, sport, country, tournament, SEASON):
    if page == 1:
        link = 'https://www.oddsportal.com/{}/{}/{}-{}/results/'.format(sport, country, tournament, SEASON)
    else:
        link = 'https://www.oddsportal.com/{}/{}/{}-{}/results/#/page/{}'.format(sport, country, tournament, SEASON,
                                                                                 page)
    DATA = []

    content1 = get_links(link, page)
    if content1 != None:
        DATA.extend(content1)

    content2 = get_links(link, page)
    if content2 != None:
        DATA.extend(content2)

    print(DATA)
    link_set = set(DATA)
    return link_set


def scrape_current_tournament_typeA(sport, tournament, country, SEASON, max_page):
    global driver
    ############### NOW WE SEEK TO SCRAPE THE ODDS AND MATCH INFO################################
    DATA_ALL = []
    for page in range(1, max_page):
        print('We start to scrape the page n°{}'.format(page))
        try:
            driver.quit()  # close all windows
        except:
            pass

        driver = webdriver.Chrome(executable_path=DRIVER_LOCATION, options=options)
        data = scrape_page_typeA(page, sport, country, tournament, SEASON)

        DATA_ALL = DATA_ALL + [y for y in data if y != None]
        driver.close()

    data_df = pd.DataFrame(DATA_ALL)
    data_df.to_csv(f'football-{SEASON}.csv', index=False, encoding='utf-8')


def scrape_oddsportal_historical(sport, country, league, start_season, nseasons, current_season, max_page):
    # indicates whether Season is in format '2010-2011' or '2011' depends on the league)
    long_season = (len(start_season) > 6)
    Season = int(start_season[0:4])
    for i in range(nseasons):
        SEASON1 = '{}'.format(Season)
        if long_season:
            SEASON1 = '{}-{}'.format(Season, Season + 1)
        print('We start to collect season {}'.format(SEASON1))
        scrape_current_tournament_typeA(sport=sport, tournament=league, country=country, SEASON=SEASON1,
                                        max_page=max_page)
        print('We finished to collect season {} !'.format(SEASON1))
        Season += 1


def get_odds(link):
    driver = webdriver.Chrome(executable_path=DRIVER_LOCATION, options=options)
    driver.get(link)
    print('We wait 2 seconds')
    time.sleep(2)

    page_odds = []
    try:
        # Now we collect all bookmaker
        startbooker = 2
        for j in range(startbooker, 30):  # only first 10 bookmakers displayed
            # bookmaker xpath
            bookmaker = driver.find_element(By.XPATH,
                                            '/html/body/div[1]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[{}]/div[1]/a[2]/p'.format(
                                                j)).text

            home = driver.find_element(By.XPATH,
                                       '/html/body/div[1]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[{}]/div[2]/div/div/p'.format(
                                           j)).text
            draw = driver.find_element(By.XPATH,
                                       '/html/body/div[1]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[{}]/div[3]/div/div/p'.format(
                                           j)).text
            away = driver.find_element(By.XPATH,
                                       '/html/body/div[1]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[{}]/div[4]/div/div/p'.format(
                                           j)).text

            match = driver.find_element(By.XPATH,
                                        '/html/body/div[1]/div/div[1]/div/main/div[2]/div[3]/div[1]').text  # match teams

            final_score = driver.find_element(By.XPATH,
                                              '/html/body/div[1]/div/div[1]/div/main/div[2]/div[3]/div[2]/div[3]/div[2]/strong').text
            date = driver.find_element(By.XPATH,
                                       '/html/body/div[1]/div/div[1]/div/main/div[2]/div[3]/div[2]/div[1]/div[2]').text  # Date and time

            page_odds.append((match, bookmaker, home, draw, away, date, final_score))
    except:
        pass
    driver.close()
    driver.quit()

    print(page_odds)
    return page_odds


def get_links_in_file(file_name) -> list:
    with open(file_name) as file_in:
        lines = []
        for line in file_in:
            if len(line) < 10:
                continue
            lines.append(line)

    return lines


full_odds = []
i = 0
for season in range(2007, 2008):
    season_links = get_links_in_file(f"football-{season}-{season+1}.csv")


    for link in season_links:

        if i == 3:
            break;
        odds = get_odds(link)
        full_odds.extend(odds)
        i = i + 1

    df = pd.DataFrame(full_odds)
    df.to_csv(f'football-odds-{season}-{season+1}.csv', index=False, encoding='utf-8')

# scrape_oddsportal_historical(
#     sport='football', country='england',
#     league='premier-league',
#     start_season='2008-2022', nseasons=14,
#     current_season='no',
#     max_page=9)
