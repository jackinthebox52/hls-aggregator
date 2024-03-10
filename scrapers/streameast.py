from bs4 import BeautifulSoup
from datetime import datetime
import requests
import argparse
import re


SCHEDULE_URLS = ['https://streameast.top/boxing/schedule', 'https://streameast.top/mma/schedule']

"""
Finds an event in the schedule based on the given query and URL.
Args:
    query (list): A list of keywords to search for in the event names.
    url (str): The URL of the schedule page to scrape.
    strict (bool, optional): If True, performs a strict search where all keywords must be present in the event name. 
                                If False, performs a loose search where any keyword can be present in the event name. 
                                Defaults to False.
Returns:
    list or None: A list containing the event name and its URL if found, or None if no event matches the query.
"""
def find_event(query: list, url: str, strict: bool=False):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    competitions = soup.find_all('a', {'class': 'competition'})
    text, match, datetime_str = None, None, None
    for competition in competitions:
        text = competition.get_text(strip=True)
        match, datetime_str = text.rsplit('- ', 1)
        match = match.strip().lower()
        date_str, time_str = datetime_str.strip().split(' ', 1)
        match_url = re.findall(r"https?://streameast\.top/match/[\w-]+/[\w'.-]+/\d+", str(competition))
        if not match_url:
            continue
        match_url = match_url[0]
        if 'today' in query:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if entry_date != datetime.today().date():
                print('Not today')
                continue    #Skip if not today
            return [match, match_url]
        
        if strict:
            if all(x in match for x in query):
                return [match, match_url]
            continue
        else:
            if any(x in match for x in query):
                return [match, match_url]
            continue
    return None

"""
Makes a request to the match_url and returns the HLS URL.
Args:
    match_url (str): The URL of the match page.
Returns:
    str: The HLS URL of the match.
Raises:
    ValueError: If no iframe or m3u8 URL is found on the match page.
"""
def get_hls_url(match_url: str):
    html = requests.get(match_url).text
    soup = BeautifulSoup(html, 'html.parser')
    iframe = soup.find('iframe', attrs={'src': re.compile(r'^https://embedstreamgate\.com/embed\?key=\d+$')})
    if not iframe:
        raise ValueError('No iframe found at ' + match_url)
    iframe_url = iframe['src']
    html = requests.get(iframe_url).text
    m3u8_url = re.findall(r'https://[\w-]+\.azureedge\.net/live/[\w-]+/playlist\.m3u8', html)
    if m3u8_url:
        return m3u8_url[0]
    raise ValueError('No m3u8 URL found at ' + iframe_url)

"""
Searches for a match in the schedule and returns the HLS URL for the first stream found.
Args:
    query (str): The query to search for in the event names.
    sport (str): The sport to search for (boxing or mma).
    strict (bool, optional): If True, performs a strict search where all keywords must be present in the event name. 
                                If False, performs a loose search where any keyword can be present in the event name. 
                                Defaults to False.
Returns:
    str: The HLS URL of the first stream found.
Raises:
    ValueError: If the sport is invalid or no event matches the query.
"""
def main(query: str, sport: str, strict: bool=False):
    query = query.lower().split()
    url = None
    match sport.lower():
        case 'boxing':
            url = SCHEDULE_URLS[0]
        case 'mma':
            url = SCHEDULE_URLS[1]
        case _:
            raise ValueError('Invalid sport')
    entry = find_event(query, url, strict)
    if not entry:
        raise ValueError('No event found')

    hls_url = get_hls_url(entry[1])
    return hls_url



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for a match in the schedule')
    parser.add_argument('--sport', type=str, required=True, help='The sport to search for')
    parser.add_argument('--query', type=str, required=True, help='The query to search for')
    parser.add_argument('-t', '--strict', action='store_true', help='Use strict search')
    args = parser.parse_args()

    url = main(args.query, args.sport, args.strict)
    print(url)
