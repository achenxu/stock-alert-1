# Stock-Alert

It appears that most, if not all stock apps in the market provide alerts based on an absolute price or % price change. It is better as a passive investor to have alerts based on changes of price in relation to metrics like 52-week low or below NAV or some other metrics.

Therefore, this script aims to achieve that. It uses python to obtain price and metrics information from SGX Stockfacts website and if meet the conditions, an alert message will be sent to the messenging app Slack.

### Dependencies
 * Python 3.6: selenium, BeautifulSoup, SlackClient

 * Chromedriver

 * Slack application