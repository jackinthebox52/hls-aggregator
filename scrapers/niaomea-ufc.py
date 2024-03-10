from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def headers_intercept(request):
    passed = False
    for host in ['niaomea.me', 'edgking.me', 'web3-lab.com', 'walletkeyslocker.me']:
        if host in request.host:
            passed = True
    if not passed:  
        #print('Aborted request: ' + request.url + ' to ' + request.host.split('.', 1)[1])
        request.abort()
        return
    
    if 'edgking.me' in request.url:
        print('Stream URL: ' + request.url)
        return

    if 'niaomea.me' in request.url:
        if 'sd0embed/UFC' in request.url:
            request.method = 'POST'
            request.params = {'pid': '5', 'gt': 'UFC+Events+|+Ultimate+Fighting+Championship', 'gc': 'UFC', 'v': 'ufc1hd~ufc1sd'}
        request.headers['Referer'] = 'https://embedstreams.me/'
        request.headers['Origin'] = 'https://embedstreams.me'
        return


options = webdriver.FirefoxOptions()
options.add_argument("--window-size=1920,1080")
options.set_capability("moz:firefoxOptions", {'log': 'TRACE'})

driver = webdriver.Firefox()
driver.request_interceptor = headers_intercept


driver.get('https://www.niaomea.me/sd0embed/UFC')
try:
    elem = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div[13]/div[1]/div/div/div[2]/div')) #This is a dummy element
    )
    elem.click()
finally:
    timeout = 10 #seconds
    start_time = time.time()
    while time.time() < start_time + timeout:
        pass




#for entry in driver.get_log('performance'):
 #   print(str(entry) + '\n')