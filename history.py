from functions import *

global DRIVER_LOCATION
DRIVER_LOCATION = "/home/derry/Programming/Backend/Python/note/selenium/chromedriver"
from selenium.webdriver.chrome.options import Options

global options
options = Options()
options.add_argument("start-maximized")
options.binary_location = r'/usr/bin/vivaldi-stable'

scrape_oddsportal_historical(
    sport='football', country='england',
    league='premier-league',
    # start_season='2007-2022', nseasons=15,
    start_season='2007-2008', nseasons=1,
    current_season='no',
    # max_page=9
    max_page=3
)
