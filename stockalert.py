from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from slackclient import SlackClient
import json
import platform


# set chromedriver
if platform.system() == 'Windows':
    chromedriver = r'C:\xxx\MyPythonScripts\chromedriver235.exe'
else:
    chromedriver = r'/Users/xxx/MyPythonScripts/chromedriver_mac235'


# set headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver=webdriver.Chrome(chromedriver, chrome_options=options)


# slack
token = 'xxx'
slack_client = SlackClient(token)
channel_id = 'CD46UTW1K'


# stock info
companies = [('A17U','Ascendas REIT'), 
             ('C2PU', 'Parkway REIT'),
             ('S68', 'SGX'),
             ('ME8U', 'Mapletree Industrial Trust'),
             ('N2IU', 'Mapletree Commercial Trust'),
             ('J69U', 'Frasers Centrepoint Trust'),
             ('BWQU', 'Frasers Logistics & Industrial Trust'),
             ('C38U', 'Capitamall Trust'),
             ('A7RU', 'Keppel Infrastructure Trust'),
             ('AJBU', 'Keppel DC REIT')]
template_url = 'http://sgx.com/wps/portal/sgxweb/home/company_disclosure/stockfacts?page=1&code='


# send message to slack app
def send_message(channel_id, message): 
    slack_client.api_call("chat.postMessage", 
                          channel=channel_id, 
                          text=message, 
                          username='sgx-alert')

# main script, webscrape for data
for code, company in companies:
    print('scanning {}...'.format(company))

    url = '{}{}'.format(template_url,code)
    driver.get(url)

    # read from iframe
    iframeElement = driver.find_element_by_tag_name('iframe')
    driver.switch_to.frame(iframeElement)
    html = driver.page_source.encode('utf-8')

    # cook the soup
    soup = BeautifulSoup(html, 'html.parser')
    tabcontent = soup.select('div .normal.right')
    
    # retrieve metrics from SGX
    previous_open_price = tabcontent[0].getText()
    previous_high_low = tabcontent[1].getText()
    previous_close_price = tabcontent[2].getText()
    week_52_high_low = tabcontent[5].getText()
    week_52_low = float(week_52_high_low.split(' ')[2])
    price_book = float(tabcontent[16].getText())
    dividend_yield = tabcontent[18].getText()
    current_price = float(soup.select('span .price')[1].getText())


    # set alert conditions
    link = 'More in SGX StockFacts {}'.format(url)
    if current_price <= week_52_low:
        message = '~~{}~~\nCurrent Price (${}) has reached 52-week low $({})!\n{}'.format(company, current_price, week_52_low, link)
        send_message(channel_id, message)
        send_message(channel_id, '\n')
    if price_book <= 1:
        message = '~~{}~~\nCurrent Price (${}) is below price-book ratio at {}!\n{}'.format(company, current_price,price_book, link)
        send_message(channel_id, message)
        send_message(channel_id, '\n')

