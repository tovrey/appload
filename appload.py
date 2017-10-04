from requests import request
from json import dumps
from sys import argv, exit
from lxml.html import fromstring


if len(argv) < 2:
    print("Playlist ID is required")
    # exit()
    PLID = "pl.393fca1ccb1441878aca980cc71a2d1c"
else:
    PLID = argv[1]

APPLE_ROOT_XPATH = ".//*[@id='tracks']/table"
APPLE_LINK = "http://tools.applemusic.com/embed/v1/playlist/" + PLID

HEADERS={"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)" +
        " Chrome/41.0.2228.0 Safari/537.36",
        "Cookie": "__cfduid=da2a0b6a443dfd1beec1b0fd74824443b1507043040;" +
        " PHPSESSID=op4b0844jre535ukb7j24ueg12; zvAuth=1; zvLang=0; notice=1;" +
        " _ga=GA1.2.640448957.1507043041; _gid=GA1.2.1514379354.1507043041;" +
        " _ym_uid=1507043041384058962; _ym_isad=2",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

APPLE_CONTENT = request("GET", APPLE_LINK, headers=HEADERS).content
APPLE_TREE = fromstring(APPLE_CONTENT)
TRACKS = APPLE_TREE.xpath(APPLE_ROOT_XPATH)
PLAYLIST = []
for track, num in zip(TRACKS, range(1, len(TRACKS) + 1)):
    new_track = {}
    new_track['pl-num'] = str(num)
    new_track['data-id'] = track.get('data-id')
    new_track['title'] = track.xpath('tr/td[2]/div[1]/div[1]/text()')[0].strip()
    new_track['artist'] = track.xpath('tr/td[2]/div[2]/text()')[0].strip()
    new_track['audio'] = track.xpath('tr/td[1]/div/div')[0].get('data-url')
    PLAYLIST.append(new_track)

print(dumps(PLAYLIST, indent=4, ensure_ascii=False))
