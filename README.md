# Stock-Alert

It appears that most, if not all stock apps in the market provide alerts only based on an absolute price being reached or % price change. It will make more sense as a passive investor to have alerts based on changes of price in relation to metrics like 52-week low, below NAV of 1, or of a certain dividend yield.

This script aims to achieve that. It uses python to obtain price and metrics information from SGX Stockfacts website and if conditions are met, an alert message will be sent to the messenging app Slack. Yahoo Finance API via `pandas_datareader` is also used to draw and post charts into Slack.

### Dependencies
 * Python 3.6: `selenium, BeautifulSoup, SlackClient, pandas_datareader, matplotlib, pandas`

 * Chromedriver

 * Slack application


 ![screenshot](https://github.com/mapattacker/stock-alert/blob/master/slack_image.png)