import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter


URL = "https://lol.gamepedia.com/{}/2019_Season/{}/Match_History"
LEAGUES = ["LCS", "LEC", "LCK", "LPL", "LMS"]
SEASONS = ["Spring Season", "Spring Playoffs",
           "Summer_Season", "Summer_Playoffs", "Regional_Finals"]


def extract_date(html):
    data = html.find_all(
        "td", attrs={"class": "mhgame-result"}
    )

    date_list = []
    for i, row in enumerate(data):
        if i % 5 == 0:
            date_list.append(row.get_text())

    return date_list


def extract_picks(html):
    data = html.find_all(
        "span", attrs={"class": "sprite champion-sprite"}
    )

    picks_list = []
    picks = []
    for i, attr in enumerate(data):
        locations = attr["style"].split(";")[0].split(":")[-1]
        x = int(locations.split(" ")[0].replace("px", "").replace("-", ""))
        y = int(locations.split(" ")[1].replace("px", "").replace("-", ""))
        if i % 20 == 19:
            picks.append((x, y))
            picks_list.append(picks)
            picks = []
        elif i % 20 >= 15:
            picks.append((x, y))
        elif i % 20 == 14:
            picks.append((x, y))
            picks_list.append(picks)
            picks = []
        elif i % 20 >= 10:
            picks.append((x, y))

    return picks_list


def convert_to_champions(picks_list):
    df = pd.read_csv("champions_img_locations.csv")
    for i, picks in enumerate(picks_list):
        for j, locations in enumerate(picks):
            champion_name = df.loc[
                (df["position_x"] == locations[0])
                & (df["position_y"] == locations[1]),
                "champions"
            ].values[0]
            picks_list[i][j] = champion_name

    return picks_list


def concat_lists(date_list, picks_list, league):
    matches_list = []
    for i, picks in enumerate(picks_list):
        match = []
        match.append(date_list[int(np.floor(i / 2))])
        match.append(league)
        for pick in picks:
            match.append(pick)
        matches_list.append(match)

    return matches_list


def get_match_picks():
    data = []
    for league in LEAGUES:
        for season in SEASONS:
            resp = requests.get(URL.format(league, season))
            html = BeautifulSoup(resp.text, "html.parser")
            date_list = extract_date(html)
            picks_list = extract_picks(html)
            picks_list = convert_to_champions(picks_list)
            picks_list = concat_lists(date_list, picks_list, league)
            data.extend(picks_list)

    url_championship = "https://lol.gamepedia.com/" \
                       "2019_Season_World_Championship/Match_History"
    resp = requests.get(url_championship)
    html = BeautifulSoup(resp.text, "html.parser")
    date_list = extract_date(html)
    picks_list = extract_picks(html)
    picks_list = convert_to_champions(picks_list)
    picks_list = concat_lists(date_list, picks_list, "WCS")
    data.extend(picks_list)

    return data


def save_match_picks(data):
    df = pd.DataFrame(
        data,
        columns=["date", "league", "top", "jungle", "mid", "bottom", "support"]
    )
    df.to_csv("match_picks.csv", index=False)


if __name__ == "__main__":
    data = get_match_picks()
    save_match_picks(data)
