from requests import request
from sys import argv, exit
from os import mkdir
from os.path import exists
from lxml.html import fromstring


if len(argv) < 2:
    print("Playlist ID is required")
    # exit()
    PLID = "pl.393fca1ccb1441878aca980cc71a2d1c"
else:
    PLID = argv[1]

APPLE_TRACKS_XPATH = ".//*[@id='tracks']/table"
APPLE_PL_NAME_XPATH = ".//*[@id='playlistHero']/table/tr/td[2]/div[1]/a/text()"
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

    
def gen_apple_pl(plid):
    playlist = {}
    playlist['id'] = plid
    playlist['name'] = str(APPLE_TREE.xpath(APPLE_PL_NAME_XPATH)[0].strip())
    playlist['tracks'] = []
    tracks = APPLE_TREE.xpath(APPLE_TRACKS_XPATH)
    for track, num in zip(tracks, range(1, len(tracks) + 1)):
        new_track = {}
        new_track['pl-num'] = str(num).rjust(len(str(len(tracks))), '0')
        new_track['data-id'] = track.get('data-id')
        new_track['title'] = track.xpath('tr/td[2]/div[1]/div[1]/text()')[0].strip()
        new_track['artist'] = track.xpath('tr/td[2]/div[2]/text()')[0].strip()
        new_track['audio-url'] = track.xpath('tr/td[1]/div/div')[0].get('data-url')
        playlist['tracks'].append(new_track)
    return playlist


def download_track(link, number, artist, title, dir_name):
    if not exists(dir_name):
        mkdir(dir_name)
    file_name = number + ". " + artist + " - " + title + ".mp3"
    bad_symbols = ["/", "\\"]
    for symbol in bad_symbols:
        if symbol in file_name:
            file_name = file_name.replace(s, "_")
    full_path = dir_name + "/" + file_name
    with open(full_path, 'wb') as f:                                                                               
        f.write(request("GET", link, headers=HEADERS).content)
    return True


def main():
    """docstring for main"""
    playlist = gen_apple_pl(PLID)
    for track in playlist['tracks']:
        download_track(track['audio-url'], track['pl-num'], track['artist'], track['title'],
                playlist['name'])
        print('Track "' + track['title'] + '" is downloaded')
    

if __name__ == '__main__':
    main()
