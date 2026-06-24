from copy import deepcopy
#from IPython.display import HTML, display

# ===================================
# 2節終了時点
# ===================================
teams = {
    "BRA": {
        "name": "ブラジル",
        "flag": "🇧🇷",
        "points": 4,
        "gd": 3,
        "gf": 4,
        "tcs": -3,
        "rank": 1
    },
    "MAR": {
        "name": "モロッコ",
        "flag": "🇲🇦",
        "points": 4,
        "gd": 1,
        "gf": 2,
        "tcs": -1,
        "rank": 2
    },
    "HTI": {
        "name": "ハイチ",
        "flag": "🇭🇹",
        "points": 0,
        "gd": -4,
        "gf": 0,
        "tcs": -4,
        "rank": 4
    },
    "SCO": {
        "name": "スコットランド",
        "flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "points": 3,
        "gd": 0,
        "gf": 1,
        "tcs": -4,
        "rank": 3
    }
}

# ===================================
# 2節終了時の試合結果
# ===================================
finished_matches = [
    {"home":"BRA","away":"MAR","home_goals":1,"away_goals":1},
    {"home":"HTI","away":"SCO","home_goals":0,"away_goals":1},
    {"home":"BRA","away":"HTI","home_goals":3,"away_goals":0},
    {"home":"MAR","away":"SCO","home_goals":1,"away_goals":0}
]

import requests
from bs4 import BeautifulSoup
import re

from datetime import datetime
from zoneinfo import ZoneInfo

# ===================================
# Yahoo速報URL
# ===================================
URL_MAP = {
    "https://soccer.yahoo.co.jp/wcup/category/2026/game/2026062402/text": {
        "home": "MAR",
        "away": "HTI",
        "home_name": "モロッコ",
        "away_name": "ハイチ"
    },

    "https://soccer.yahoo.co.jp/wcup/category/2026/game/2026062401/text": {
        "home": "SCO",
        "away": "BRA",
        "home_name": "スコットランド",
        "away_name": "ブラジル"
    }
}

# ===================================
# Yahoo速報から1試合取得
# ===================================
def get_match_info(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)

    home = URL_MAP[url]["home"]
    away = URL_MAP[url]["away"]
    home_name = URL_MAP[url]["home_name"]
    away_name = URL_MAP[url]["away_name"]

    # ----------------------------
    # 試合前
    # ----------------------------
    if res.status_code == 404:

        return {
            "minute": "試合前",
            "home": home,
            "away": away,
            "home_goals": 0,
            "away_goals": 0,
            "home_tcs": 0,
            "away_tcs": 0
        }

    soup = BeautifulSoup(res.text, "html.parser")

    # ----------------------------
    # 試合中
    # ----------------------------
    live = soup.find(
        class_="sc-scoreList__item sc-scoreList__item--live"
    )

    if live:

        text = live.get_text(" ", strip=True)

        m = re.search(
            r'(\d+)\s*-\s*(\d+)\s*(.+)$',
            text
        )

        home_goals = int(m.group(1))
        away_goals = int(m.group(2))
        minute = m.group(3)

    # ----------------------------
    # 試合終了
    # ----------------------------
    else:

        minute = "試合終了"

        home_goals = 0
        away_goals = 0

        for tag in soup.find_all(class_="sc-textLive"):

            text = tag.get_text(" ", strip=True)

            if "試合終了" not in text:
                continue

            m = re.search(r'(\d+)-(\d+)', text)

            if m:
                home_goals = int(m.group(1))
                away_goals = int(m.group(2))
                break

    # ----------------------------
    # TCS
    # ----------------------------
    home_tcs = 0
    away_tcs = 0

    for item in soup.find_all(class_="sc-textLive__item"):

        name_tag = item.find(class_="sc-textLive__name")
        text_tag = item.find(class_="sc-textLive__text")

        if name_tag is None or text_tag is None:
            continue

        team_name = name_tag.get_text(strip=True)
        event_text = text_tag.get_text(strip=True)

        point = 0

        if "イエローカード" in event_text:
            point -= 1

        if "レッドカード" in event_text:
            point -= 4

        if "退場" in event_text:
            point -= 1

        if point == 0:
            continue

        if team_name == home_name:
          home_tcs += point

        elif team_name == away_name:
          away_tcs += point

    return {
        "minute": minute,
        "home": home,
        "away": away,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "home_tcs": home_tcs,
        "away_tcs": away_tcs
    }

# ===================================
# スクレイピング実行判定
# ===================================
now = datetime.now(ZoneInfo("Asia/Tokyo"))

start_time = datetime(2026, 6, 25, 6, 59,
                      tzinfo=ZoneInfo("Asia/Tokyo"))

# 念のための自動更新打ち切り時刻
end_time = datetime(2026, 6, 25, 14, 0,
                      tzinfo=ZoneInfo("Asia/Tokyo"))

scraping_enabled = (
    now >= start_time
    and now < end_time
)

# ===================================
# 最終節の途中経過（Yahoo速報取得）
# ===================================
if scraping_enabled:

    live_matches = [
        get_match_info(
            "https://soccer.yahoo.co.jp/wcup/category/2026/game/2026062402/text"
        ),
        get_match_info(
            "https://soccer.yahoo.co.jp/wcup/category/2026/game/2026062401/text"
        )
    ]

else:

    # 試合前はスクレイピングしない
    live_matches = [
        {
            "minute":"試合前",
            "home":"MAR",
            "away":"HTI",
            "home_goals":0,
            "away_goals":0,
            "home_tcs":0,
            "away_tcs":0
        },
        {
            "minute":"試合前",
            "home":"SCO",
            "away":"BRA",
            "home_goals":0,
            "away_goals":0,
            "home_tcs":0,
            "away_tcs":0
        }
    ]

# ===================================
# ステータス判定
# ===================================
minutes = [m["minute"] for m in live_matches]

# ①試合前
if all(x == "試合前" for x in minutes):
    status = "試合前"

# ②試合終了
elif all(x == "試合終了" for x in minutes):
    status = "試合終了"

# ③それ以外＝試合中
else:
    status = "試合中"

# 自動更新判定
# 6:59以降のみ有効
# 試合終了または14:00で停止
auto_refresh = (
    now >= start_time
    and status != "試合終了"
    and now < end_time
)

# ===================================
# 成績更新
# ===================================
table = deepcopy(teams)

for match in live_matches:

    home = match["home"]
    away = match["away"]
    hg = match["home_goals"]
    ag = match["away_goals"]

    # 得点
    table[home]["gf"] += hg
    table[away]["gf"] += ag

    # 得失点差
    table[home]["gd"] += hg - ag
    table[away]["gd"] += ag - hg

    # TCS
    table[home]["tcs"] += match["home_tcs"]
    table[away]["tcs"] += match["away_tcs"]

    # 勝点
    if status != "試合前":

      if hg > ag:
        table[home]["points"] += 3
      elif hg < ag:
        table[away]["points"] += 3
      else:
        table[home]["points"] += 1
        table[away]["points"] += 1

# ===================================
# 全試合（終了済＋現在スコア）
# ===================================
all_matches = finished_matches.copy()

for m in live_matches:
    all_matches.append({
        "home": m["home"],
        "away": m["away"],
        "home_goals": m["home_goals"],
        "away_goals": m["away_goals"]
    })

# ===================================
# 2チーム間の直接対戦成績
# ===================================
def head_to_head(team1, team2):

    p1 = p2 = 0
    gd1 = gd2 = 0
    gf1 = gf2 = 0

    for m in all_matches:

        home = m["home"]
        away = m["away"]

        if set([home, away]) != set([team1, team2]):
            continue

        hg = m["home_goals"]
        ag = m["away_goals"]

        if home == team1:

            gf1 += hg
            gf2 += ag

            gd1 += hg - ag
            gd2 += ag - hg

            if hg > ag:
                p1 += 3
            elif hg < ag:
                p2 += 3
            else:
                p1 += 1
                p2 += 1

        else:

            gf1 += ag
            gf2 += hg

            gd1 += ag - hg
            gd2 += hg - ag

            if ag > hg:
                p1 += 3
            elif ag < hg:
                p2 += 3
            else:
                p1 += 1
                p2 += 1

    return {
        team1: (p1, gd1, gf1),
        team2: (p2, gd2, gf2)
    }

# ===================================
# 簡易順位計算
# （勝点→直接対決→得失点差→総得点）
# ===================================
teams_list = list(table.keys())

# まず全体成績でソート
teams_list.sort(
    key=lambda t: (
        table[t]["points"],
        table[t]["gd"],
        table[t]["gf"],
        table[t]["tcs"],
        -table[t]["rank"]
    ),
    reverse=True
)

# 同勝点の2チームだけ直接対戦で修正
for i in range(len(teams_list)-1):

    t1 = teams_list[i]
    t2 = teams_list[i+1]

    if table[t1]["points"] != table[t2]["points"]:
        continue

    h2h = head_to_head(t1, t2)

    key1 = (
    h2h[t1][0],      # 当該勝点
    h2h[t1][1],      # 当該得失点差
    h2h[t1][2],      # 当該得点
    table[t1]["gd"], # 全体得失点差
    table[t1]["gf"], # 全体得点
    table[t1]["tcs"],# TCS
    -table[t1]["rank"] # FIFA順位
    )

    key2 = (
    h2h[t2][0],
    h2h[t2][1],
    h2h[t2][2],
    table[t2]["gd"],
    table[t2]["gf"],
    table[t2]["tcs"],
    -table[t2]["rank"]
    )

    if key2 > key1:
        teams_list[i], teams_list[i+1] = teams_list[i+1], teams_list[i]

# ===================================
# 順位表タイトル
# ===================================
title = "順位表（" + status + "）"

# ===================================
# HTML作成
# ===================================
html = """
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
"""

if auto_refresh:
    html += '<meta http-equiv="refresh" content="60">'

html += """
<style>

body{
max-width:480px;
margin:auto;
padding:8px;
box-sizing:border-box;
font-family:sans-serif;
}

h1{
text-align:center;
font-size:32px;
}

h2{
font-size:24px;
}

.scorebox{
font-size:22px;
text-align:center;
margin-bottom:20px;
}

.match{
margin-bottom:16px;
}

table{
width:100%;
border-collapse:collapse;
font-size:18px;
}

th,td{
border:1px solid #cccccc;
padding:6px 2px;
text-align:center;
}

.team{
white-space:nowrap;
text-align:left;
}

.note{
font-size:14px;
line-height:1.8;
text-align:left;
}

@media (max-width:480px){

h1{
font-size:28px;
}

h2{
font-size:20px;
}

.scorebox{
font-size:18px;
}

table{
font-size:16px;
}

th,td{
padding:4px 1px;
}

.note{
font-size:12px;
}

}

</style>



</head>

<body>

<h1>C組 LIVE順位</h1>

<div class="scorebox">
"""

#Google Analyticsのグローバルサイトタグを追加予定（</style>の下の行）

# スコア表示
for m in live_matches:

    home = teams[m["home"]]
    away = teams[m["away"]]

    html += (
    "<div class='match'>"
    + str(m["minute"])
    + "<br>"
    + home["flag"]
    + " "
    + str(m["home_goals"])
    + " - "
    + str(m["away_goals"])
    + " "
    + away["flag"]
    )
    # モロッコのみ表示
    if m["home"] == "MAR":
      html += (
          "<br>"
          + "(TCS: "
          + home["flag"]
          + " "
          + str(m["home_tcs"])
          + ")"
          + "<br>"
          + "---"
      )
    # ブラジルのみ表示
    elif m["away"] == "BRA":
      html += (
          "<br>"
          + "(TCS: "
          + away["flag"]
          + " "
          + str(m["away_tcs"])
          + ")"
      )

html += "</div>"

# 順位表
html += (
    "<h2>"
    + title +
    "</h2>"

    "<table>"

    "<tr>"
    "<th>順位</th>"
    "<th>チーム</th>"
    "<th>勝点</th>"
    "<th>得失差</th>"
    "<th>得点</th>"
    "<th>TCS</th>"
    "</tr>"
)

for i, team in enumerate(teams_list, start=1):

    data = table[team]

    html += (
        "<tr>"
        + "<td>" + str(i) + "</td>"
        + "<td class='team'>" + data["flag"] + " " + data["name"] + "</td>"
        + "<td>" + str(data["points"]) + "</td>"
        + "<td>" + str(data["gd"]) + "</td>"
        + "<td>" + str(data["gf"]) + "</td>"
        + "<td>" + str(data["tcs"]) + "</td>"
        + "</tr>"
    )

html += """
</table>

<br>

<div class="note">
<b>順位決定方法</b><br>
①勝点<br>
②直接対決<br>
③得失点差<br>
④得点<br>
⑤TCS（フェアプレーポイント）※<br>
※警告1枚: -1、警告2枚の退場: -3、一発退場: -4<br>
<br>
【正式結果は公式サイトを確認下さい】
</div>

</body>
</html>
"""

# ===================================
# index.html保存
# ===================================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# ===================================
# Colab上で表示
# ===================================
#display(HTML(html))

#print("index.html を生成しました。")

# index.html保存
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html generated")

