import pandas as pd

with open('football-odds-2007-2008.csv') as file_in:
    lines = []
    for line in file_in:
        lines.append(line)


def parse_bookmaker_odds_date_score(csv_data):
    parts = csv_data.split(',')
    bookmaker = parts[1]
    home_odds = parts[2]
    draw_odds = parts[3]
    away_odds = parts[4]
    date = parts[6]
    score = parts[8].replace('\n', "")

    return (bookmaker, date, home_odds, draw_odds, away_odds, score)


def subsplit_list(start, step, target_list):
    return target_list[start::step]


def create_dataframe(split_list):
    full_data = []
    for each in split_list:
        bookie_tuple = parse_bookmaker_odds_date_score(each)
        full_data.append(bookie_tuple)

    return pd.DataFrame(full_data)


df = pd.read_csv('football-odds-2007-2008.csv')
print(df)