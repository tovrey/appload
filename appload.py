from requests import request
from sys import argv, exit
from os import mkdir
from os.path import exists
from lxml.html import fromstring


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

APPLE_LINK = "http://tools.applemusic.com/embed/v1/playlist/" 
APPLE_TRACKS_XPATH = ".//*[@id='tracks']/table"
APPLE_PL_NAME_XPATH = ".//*[@id='playlistHero']/table/tr/td[2]/div[1]/a/text()"
LIMIT_APPLE_TRACKS = 1000
ZF_SITE = "https://zf.fm"
ZF_SEARCH_LINK = "https://zf.fm/mp3/search?keywords="
ZF_RESULT_XPATH = ".//*[@id='container']/div[1]/div[2]/div/div/div[4]/div/div"
LIMIT_MATCH_TRACKS = 20

def get_plid():
    if len(argv) < 2:
        print("Playlist ID is required")
        exit()
    else:
        plid = argv[1]
    return plid
    

def gen_apple_pl(plid):
    playlist = {}
    playlist['id'] = plid
    apple_link = APPLE_LINK + plid
    apple_content = request("GET", apple_link, headers=HEADERS).content
    apple_tree = fromstring(apple_content)
    playlist['name'] = str(apple_tree.xpath(APPLE_PL_NAME_XPATH)[0].strip())
    playlist['tracks'] = []
    tracks = apple_tree.xpath(APPLE_TRACKS_XPATH)
    for track, num in zip(tracks, range(1, len(tracks) + 1)):
        new_track = {}
        new_track['pl-num'] = str(num).rjust(len(str(len(tracks))), '0')
        new_track['data-id'] = track.get('data-id')
        new_track['title'] = track.xpath('tr/td[2]/div[1]/div[1]/text()')[0].strip()
        new_track['artist'] = track.xpath('tr/td[2]/div[2]/text()')[0].strip()
        new_track['audio-url'] = track.xpath('tr/td[1]/div/div')[0].get('data-url')
        playlist['tracks'].append(new_track)
    return playlist


def gen_zf_matchlist(artist, title):
    search_string = artist + ' ' + title
    link = ZF_SEARCH_LINK + search_string
    result = []
    zf_content = request("GET", link, headers=HEADERS).content
    zf_tree = fromstring(zf_content)
    tracks = zf_tree.xpath(ZF_RESULT_XPATH)
    tracks = tracks[:LIMIT_MATCH_TRACKS]
    for track, num in zip(tracks, range(1, len(tracks) + 1)):
        new_track = {}
        new_track['match-num'] = str(num).rjust(len(str(len(tracks))), '0')
        new_track['time'] = track.xpath("div/div/div[1]/span/text()")[0].strip()
        new_track['zf-id'] = track.xpath("div/div/span")[0].get('data-sid')
        new_track['title'] = track.xpath("div/div/div[2]/div[2]/a/span/text()")[0].strip()
        new_track['artist'] = track.xpath("div/div/div[2]/div[1]/a/span/text()")[0].strip()
        new_track['url'] = track.xpath("div/div/span")[0].get('data-url')
        result.append(new_track)
    return result


def choose_from(matchlist):
    for track in matchlist:
        infostring = '{}. {} - "{}" ({})'.format(track['match-num'], track['artist'],
                track['title'], track['time'])
        print(infostring)
    choise = input("Choose track for downloading:\n")
    if not choise:
        choise = 1
    choise = int(choise)
    return matchlist[choise - 1]
    
def download_track(link, number, artist, title, dir_name):
    if not exists(dir_name):
        mkdir(dir_name)
    file_name = number + ". " + artist + " - " + title + ".mp3"
    bad_symbols = ["/", "\\"]
    for symbol in bad_symbols:
        if symbol in file_name:
            file_name = file_name.replace(s, "_")
    full_path = dir_name + "/" + file_name
    if link.startswith("/"):
        link = ZF_SITE + link
    with open(full_path, 'wb') as f:
        f.write(request("GET", link, headers=HEADERS).content)
    print('Track "' + artist + ' - ' + title + '" is downloaded')
    return True


def main():
    plid = get_plid()
    apple_pl = gen_apple_pl(plid)
    tracks = apple_pl['tracks'][:LIMIT_APPLE_TRACKS]
    for track in tracks:
        matchlist = gen_zf_matchlist(track['artist'], track['title'])
        matchtrack = choose_from(matchlist)
        download_track(matchtrack['url'], track['pl-num'], track['artist'], track['title'],
                apple_pl['name'])
    

if __name__ == '__main__':
    main()
