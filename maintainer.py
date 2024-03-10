'''Maintains the specified number of hls streams with the integrated scrapers'''
import argparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapers.streameast as streameast
import time, os
from collections import deque

def browser_visit(url: str):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)  # Start the WebDriver session
    driver.install_addon('etc/uBlock0_1.56.1b14.firefox.signed.xpi', temporary=False)  # Install the extension
    time.sleep(2)
    driver.get(url)
    #Wait till page loads then get al;l; items on page with class "clickable"
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/head")))
        driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe'))
        driver.find_element(By.ID, 'player').click()
        time.sleep(1)
    except Exception as e:
        print(e)
        print('Page load timeout')
    driver.quit()
    return

def maintain(hls: str, event_url: str):
    start_time = time.time()
    ffmpeg_failed = True
    failed_time = None
    failed_amount = 0
    while start_time + 3600 > time.time():
        print('Maintaining the stream')
        if ffmpeg_failed:
            browser_visit(event_url)
            os.system(f'cmd/ffmpeg.sh {hls} &')
            ffmpeg_failed = False
        else:
            failed_amount = 0
            failed_time = None
        if os.path.exists('etc/error.log'):
            lines = get_last_lines('etc/error.log', 20)  # Get the last 20 lines of the error.log file
            for line in lines:
                for substring in ['error', 'failed', 'denied', '404', '403', 'timeout', 'unavailable']:
                    if substring in line:
                        print(f'FFMPEG failed at {substring} in\n{line}')
                        ffmpeg_failed = True
                        failed_amount += 1
                        print(f'Failed amount: {failed_amount}')
                        if not failed_time:
                            failed_time = time.time()
                        elif time.time() - failed_time > 300:
                            print('FFMPEG failed for too long')
                            exit(1)
                        os.system('pkill -f ffmpeg')    # TODO possibly need to flush the logs here
                        break
                
        time.sleep(5)
                

def get_last_lines(filename: str, num_lines: int) -> list:
    with open(filename, 'r') as file:
        lines = deque(file, num_lines)
    return list(lines)


def main(query: str, sport: str, strict: bool=False, link: str=None):
    event_entry = None
    if not link:
        query = query.lower().split()
        url = None
        match sport.lower():
            case 'boxing':
                url = streameast.SCHEDULE_URLS[0]
            case 'mma':
                url = streameast.SCHEDULE_URLS[1]
            case _:
                raise ValueError('Invalid sport')
        event_entry = streameast.find_event(query, url, strict)
        if not event_entry:
            raise ValueError('No event found')
    else:
        event_entry = [None, link]

    browser_visit(event_entry[1])  # Call the browser_visit function with the hls_url

    hls_url = streameast.get_hls_url(event_entry[1])

    maintain(hls_url, event_entry[1])
    print('Done')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Grab the hls url of a match, then pass into ffmpeg to restream. Uses selenium browser to visit the referrer page and authenticate our IP via websocket.')
    parser.add_argument('-l', '--link', type=str, help='The link to the match page.')
    parser.add_argument('-q', '--query', type=str, help='The query to search for in the event names.')
    parser.add_argument('-s', '--sport', type=str, help='The sport to search for (boxing or mma).')
    parser.add_argument('--strict', action='store_true', help='If True, performs a strict search where all keywords must be present in the event name. If False, performs a loose search where any keyword can be present in the event name.')
    args = parser.parse_args()
    main(args.query, args.sport, args.strict, args.link)