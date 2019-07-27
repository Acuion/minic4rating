import requests
import trueskill
from bs4 import BeautifulSoup

def pagesCount():
    page = requests.get('https://aicups.ru/round/9/?up=1#unranked-games').text
    soup = BeautifulSoup(page, 'html.parser')
    return int(soup.find("a", {"aria-label" : "Next"})['data-id'])

def getRating():
    players = set()
    rating = {}

    for pageNum in range(pagesCount(), 0, -1):
        print('Page', pageNum)
        page = requests.get('https://aicups.ru/round/9/?up={}#unranked-games'.format(pageNum)).text
        soup = BeautifulSoup(page, 'html.parser')
        games = soup.find(id='unranked-games').findAll(class_='session-item')
        for game in games:
            tds = game.findAll('td')
            if 'Проверено' != tds[2].text.strip():
                print('Is in progress')
                continue
            thisRating = list(map(lambda x: x.text.strip(), tds[5].findAll(class_='profile-link')))
            if 2 == len(thisRating):
                print('Is a duel')
                continue # duel
            if len(set(thisRating)) != len(thisRating):
                print('Players are not unique')
                continue # same players
            print('Game is ok')

            thisRates = []
            for player in thisRating:
                if player not in players:
                    rating[player] = trueskill.Rating()
                    players.add(player)
                thisRates.append((rating[player],))
            thisRates = trueskill.rate(thisRates)
            for (player, rate) in zip(thisRating, thisRates):
                rating[player] = rate[0]

    return rating

rating = getRating()
sortedRating = sorted(rating.items(), key=lambda kv: trueskill.expose(kv[1]), reverse=True)

result = ""
for (num, rate) in enumerate(sortedRating):
    result += '{}) {} ({})\n'.format(num + 1, rate[0], str(rate[1]))
with open('rating.txt', 'w', encoding='utf8') as f:
    f.write(result)
