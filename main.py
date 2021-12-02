from requests.api import head
from requests.sessions import InvalidSchema
import undetected_chromedriver.v2 as uc
from selenium.webdriver import Firefox, Chrome, Edge
import requests, time
from EventOdder import EventOdder



# target_url = "https://sports.bwin.es/es/sports/directo/f%C3%BAtbol-4"
target_url = "https://sports.bwin.es/es/sports/directo/f%C3%BAtbol-4?fallback=false"

""" Extract and parse live data."""


driver = uc.Chrome()
# driver = uc.Chrome(headless=True)
driver.maximize_window()
driver.get(target_url)
time.sleep(5)




event_urls = []
live = driver.find_elements_by_xpath('//*[contains(@class, "event-group")]')



for l in live:
    event_urls.append(l.find_element_by_xpath('.//*[contains(@class, "grid-info-wrapper")]').get_attribute('href') + '?market=-1')


for url in event_urls:
    driver.get(url)
    time.sleep(3.4)
    event_odder = EventOdder(driver)
    input('Odder done!')
    # scrape odds data







# live_contatiner = driver.find_element_by_xpath('//*[contains(@class, "grid-live-favourite")]')
# for el in live_contatiner.find_elements_by_xpath('.//*[contains(@class, "grid-event")]'):
#     print(el)



input()
