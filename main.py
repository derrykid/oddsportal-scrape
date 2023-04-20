#!/usr/bin/env python3
from scrap_func import *
import os

scrape_sport_links_main(sport='basketball',
                        country='usa',
                        league='nba',
                        start_season='2008-2022',
                        nseasons=14,
                        max_page=28)
