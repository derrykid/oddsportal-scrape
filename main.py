from ScrapFootball import *

full_odds = []
i = 0
for season in range(2007, 2008):
    games_link_all_season = read_hyperlinks_to_list(f"football-{season}-{season + 1}.csv")

    for link in games_link_all_season:
        odds = open_page_parse_html_return_odds_tuple(link)
        full_odds.extend(odds)
        i = i + 1

    df = pd.DataFrame(full_odds)
    df.to_csv(f'football-odds-{season}-{season+1}.csv', index=False, encoding='utf-8')
