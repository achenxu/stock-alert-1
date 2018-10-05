from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from slackclient import SlackClient
import json
import platform
# to generate chart
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as web
from datetime import datetime
plt.style.use('seaborn')


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
token = 'xoxp'
slack_client = SlackClient(token)
channel_id = 'CD5H7AW4W'


template_url = 'http://sgx.com/wps/portal/sgxweb/home/company_disclosure/stockfacts?page=1&code='


# send message to slack app
def send_message(channel_id, message): 
    slack_client.api_call("chat.postMessage", 
                          channel=channel_id, 
                          text=message, 
                          username='sgx-alert')
    slack_client.api_call("files.upload",
                            channels=channel_id,
                            file=chart,
                            title='price and volume chart')


def generate_chart(code, company):
    end = datetime.now()
    start = datetime(end.year-1, end.month, end.day)

    code = '{}.SI'.format(code)
    df = web.DataReader(code, 'yahoo', start, end)

    # generate moving average
    sma10 = df['Close'].rolling(10).mean() #10 days
    sma20 = df['Close'].rolling(20).mean() #20 days
    sma30 = df['Close'].rolling(30).mean() #30 days

    # create graph
    plt.figure(figsize=(10,5))
    top = plt.subplot2grid((4,4), (0, 0), rowspan=3, colspan=4)
    bottom = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)

    dfsma = pd.DataFrame({'df': df['Close'], 'SMA 10': sma10, 'SMA 20': sma20, 'SMA 30': sma30})
    top.plot(df.index, dfsma, linewidth=1)
    top.legend(['Actual','SMA 10','SMA 20','SMA 30'])
    top.set_title(company)
    bottom.bar(df.index, df['Volume'])

    # set the labels
    top.axes.get_xaxis().set_visible(False)
    # top.set_title('CapitalMall Trust')
    top.set_ylabel('Adj Closing Price')
    bottom.set_ylabel('Volume')
    plt.savefig('plot.png', dpi=200)

    chart = open('plot.png', 'rb')
    return chart


# main script, webscrape for data
def main_script(companies, template_url, driver):
    for code, company in companies:
        flag = True
        x = 0
        # sometimes scraping fail, will retry till it works
        while flag == True:
            try:
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
                week_52_high_low = tabcontent[5].getText().split('-')
                week_52_low = float(week_52_high_low[1].replace('S$ ',''))
                week_52_high = float(week_52_high_low[0].replace('S$ ',''))
                price_book = float(tabcontent[16].getText())
                dividend_yield = tabcontent[18].getText()
                current_price = float(soup.select('span .price')[1].getText())

                # create graph
                chart = generate_chart(code, company)

                # set alert conditions
                alert = []
                # 52-week low
                if current_price <= week_52_low:
                    alert.append('`Current Price at 52-week low`')
                # price-book
                if price_book <= 1:
                    alert.append('`Price level with NAV`')
                # below average
                if current_price <= average_price and average_price != 0:
                    alert.append('`Current Price below Average Price`')
                alert = '\n'.join(alert)

                message = '*{}*\n{}\n```Current Price: ${}\nAverage Price: ${}\n52-Week Low: ${}-${}\nDividend Yield: {}\nPrice-Book: {}```\n>{}'.format(company, \
                                                                                alert, current_price, average_price, week_52_low, week_52_high, dividend_yield, price_book, url)
                send_message(channel_id, message, chart)
                
                flag = False
                
            except Exception as e:
                print(e)
                x += 1
                # retry 5 times only
                if x == 5:
                    flag = False
                pass
            

# stock query
companies = [('A17U','Ascendas REIT', 0), 
             ('C2PU', 'Parkway REIT', 0),
             ('S68', 'SGX', 1),
             ('ME8U', 'Mapletree Industrial Trust', 1),
             ('N2IU', 'Mapletree Commercial Trust', 1),
             ('J69U', 'Frasers Centrepoint Trust', 1),
             ('C38U', 'Capitamall Trust', 1),
             ('A7RU', 'Keppel Infrastructure Trust', 1),
             ('AJBU', 'Keppel DC REIT', 1)]


main_script(companies, template_url, driver)