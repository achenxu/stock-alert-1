from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import platform



if platform.system() == 'Windows':
    chromedriver = r'C:\xxx\MyPythonScripts\chromedriver235.exe'
else: # linux, mac
    chromedriver = r'/Users/xxx/MyPythonScripts/chromedriver_mac235'

# set headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver=webdriver.Chrome(chromedriver, chrome_options=options)


companies = [('A17U','Ascendas REIT')]
template_url = 'http://sgx.com/wps/portal/sgxweb/home/company_disclosure/stockfacts?page=1&code='



for code, company in companies:
    url = '{}{}'.format(template_url,code)
    # while test(code,url) == '-':
    driver.get(url)
    # read from iframe
    iframeElement = driver.find_element_by_tag_name('iframe')
    driver.switch_to.frame(iframeElement)
    html = driver.page_source.encode('utf-8')

    soup = BeautifulSoup(html, 'html.parser')
    tabcontent = soup.select('div .normal.right')
    
    previous_open_price = tabcontent[0].getText()
    previous_high_low = tabcontent[1].getText()
    previous_close_price = tabcontent[2].getText()
    week_52_high_low = tabcontent[5].getText()
    week_52_low = float(week_52_high_low.split(' ')[2])
    price_book = float(tabcontent[16].getText())
    dividend_yield = tabcontent[18].getText()

    current_price = float(soup.select('span .price')[1].getText())


    if current_price <= week_52_low:
        print(company)
        print('Current Price ${} has reached 52-week low!'.format(current_price))
    if price_book <= 1:
        print(company)
        print('Current Price ${} is below price-book ratio!'.format(current_price))

