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


def extract_link_by_xpath(xpath):
    """
    Extract the links by the xpath
    """
    try:
        link = driver.find_element(By.XPATH, xpath).get_attribute('href')
        print(link)
        return link
    except:
        return False


def collect_hyperlinks_from_result_page(page, sport, country, tournament, SEASON):
    """
    collect the page links of historical match in the season. return the page links to each game
    """

    # the url to the result pages
    if page == 1:
        link = 'https://www.oddsportal.com/{}/{}/{}-{}/results/'.format(sport, country, tournament, SEASON)
    else:
        link = 'https://www.oddsportal.com/{}/{}/{}-{}/results/#/page/{}'.format(sport, country, tournament, SEASON,
                                                                                 page)

    # get hyperlinks
    game_hyperlinks = []
    content1 = get_hyperlinks_on_historical_result_as_list(link, page)
    if content1 != None:
        game_hyperlinks.extend(content1)

    content2 = get_hyperlinks_on_historical_result_as_list(link, page)
    if content2 != None:
        game_hyperlinks.extend(content2)

    print(game_hyperlinks)

    # use set to remove the duplicates
    link_set = set(game_hyperlinks)
    return link_set


def get_hyperlinks_on_historical_result_as_list(link, page):
    """
    Get the hyperlinks to every match page and return it as a list
    """

    # open the browser
    driver.get(link)

    # it's necessary to scroll the webpage because the html document at oddsportal will not display unless
    # the window is scrolling down
    # this mimics the human behaviours
    i = 0
    while i < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i = i + 1

    driver.execute_script("window.scrollTo(0, -document.body.scrollHeight);")
    time.sleep(0.3)

    links = []
    # appends the 'mark' in the data, so we can know how many links are collected in each page
    links.append(f"page:{page}")
    for i in range(1, 100):
        # There are 2 forms, I found that the first record in a day, the html path might be like 'target1'
        # the rest html path is like 'target2'
        xpath1 = '/html/body/div[1]/div/div[1]/div/main/div[2]/div[5]/div[1]/div[{}]/div/div/a'.format(i)
        xpath2 = '/html/body/div[1]/div/div[1]/div/main/div[2]/div[5]/div[1]/div[{}]/div[2]/div/a'.format(i)

        link_a = extract_link_by_xpath(xpath1)
        link_b = extract_link_by_xpath(xpath2)

        # it's either link_a exists or link_b
        if link_a or link_b:
            if link_a:
                links.append(link_a)
                continue
            else:
                links.append(link_b)

    return links


def scrape_tournament_game_links_save_as_csv(sport, tournament, country, season, max_page):
    """
    Scrape the webpage by
    1. sport
    2. tournament: e.g. Premier league, league one, league two
    3. country: England, etc
    4. season: 2011-2012, 2015-2019
    5. max-page: x, means only scrape x pages
    """

    global driver
    data_all = []
    for page in range(1, max_page):
        print('We start to scrape the page n°{}'.format(page))
        try:
            driver.quit()  # close all windows
        except:
            pass

        driver = webdriver.Chrome(executable_path=DRIVER_LOCATION, options=options)
        data = collect_hyperlinks_from_result_page(page, sport, country, tournament, season)

        data_all = data_all + [y for y in data if y is not None]
        driver.close()

    data_df = pd.DataFrame(data_all)
    data_df.to_csv(f'{sport}-{season}.csv', index=False, encoding='utf-8')


def scrape_sport_links_main(sport, country, league, start_season, nseasons, max_page):
    """
    Scrape by season. this function checks the start season and end season and scrape data
    """
    # indicates whether Season is in format '2010-2011' or '2011' depends on the league)
    long_season = (len(start_season) > 6)
    Season = int(start_season[0:4])
    for i in range(nseasons):
        SEASON1 = '{}'.format(Season)
        if long_season:
            SEASON1 = '{}-{}'.format(Season, Season + 1)
        print('We start to collect season {}'.format(SEASON1))
        scrape_tournament_game_links_save_as_csv(sport=sport, tournament=league, country=country,
                                                 season=SEASON1,
                                                 max_page=max_page)
        print('We finished to collect season {} !'.format(SEASON1))
        Season += 1


def open_page_parse_html_return_odds_tuple(link):
    """
    This function opens the match result page, parses the document, and returns the tuple of
    (bookmaker, odds, time, game, team, etc)
    """
    # power up the browser
    driver = webdriver.Chrome(executable_path=DRIVER_LOCATION, options=options)
    driver.get(link)
    print('We wait 2 seconds')
    time.sleep(2)

    odds_in_page = []
    try:
        # Now we collect all bookmaker
        html_div_start_num = 2
        for j in range(html_div_start_num, 30):  # only first 10 bookmakers displayed
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

            odds_in_page.append((match, bookmaker, home, draw, away, date, final_score))
    except:
        pass
    driver.close()
    driver.quit()

    print(odds_in_page)
    return odds_in_page


def read_file_links_scrape_odds_save_as_file(sport, from_year, to_year):
    full_odds = []
    i = 0
    for season in range(from_year, to_year):
        games_link_all_season = read_hyperlinks_to_list(f"{sport}-{season}-{season + 1}.csv")

        for link in games_link_all_season:
            odds = open_page_parse_html_return_odds_tuple(link)
            full_odds.extend(odds)
            i = i + 1

        df = pd.DataFrame(full_odds)
        df.to_csv(f'{sport}-odds-{season}-{season + 1}.csv', index=False, encoding='utf-8')


def read_hyperlinks_to_list(file_name) -> list:
    """
    In the csv file, there are the links of all games played in that season.
    These links are the hyperlinks to the game. The page has the odds of bookmakers
    """
    try:
        with open(file_name) as file_in:
            lines = []
            for line in file_in:
                if len(line) < 10:
                    continue
                lines.append(line)
    except FileNotFoundError:
        print(FileNotFoundError)
        raise RuntimeError

    return lines
