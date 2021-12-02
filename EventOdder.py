from bs4.element import ResultSet
import undetected_chromedriver.v2 as uc

from selenium.webdriver import Firefox, Chrome, Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait     
from selenium.webdriver.support import expected_conditions as EC 	
from selenium.common.exceptions import TimeoutException
import json, time

from bs4 import BeautifulSoup


class EventOdder:

    driver = None
    market_groups = []


    def __init__(self) -> None:
        self.set_driver()


    def set_driver(self):
        # driver = uc.Chrome()
        driver = uc.Chrome(headless=True)

        driver.maximize_window()
        driver.implicitly_wait(15)
        
        self.driver = driver

    def load_event_model(self):
        return json.load(open("event.json", "r"))

    def get_live_events_urls(self):
        # football live
        target_url = "https://sports.bwin.es/es/sports/directo/f%C3%BAtbol-4?fallback=false"
        self.driver.get(target_url)

        event_urls = []
        try:
            live = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'event-group')]")))
        except TimeoutException as e:
            raise Exception(f"Not football live events available")

        for l in live:
            event_urls.append(l.find_element_by_xpath(".//*[contains(@class, 'grid-info-wrapper')]").get_attribute("href") + "?market=-1")

        return event_urls

    def scrape_event_information(self, url):    
        # returns competition and participants for event of url
        
        # go to event url 
        self.driver.get(url)
        # load event model (json)
        event_model = self.load_event_model()

        # basic event data (participants and competition)
        event_model["event"], event_model["competition"] = self.scrape_participants_and_competition()

        try:
            event_model = self.get_available_markets(event_model)
        except Exception as e:
            raise Exception(f"Exception getting markets: {e}")
        return event_model

    def scrape_participants_and_competition(self):
        # with driver in event page
        try:
            participants = [el.get_attribute("innerHTML").strip() for el in WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "participant-name-value")))] 
            event_string = f"{participants[0].split('<')[0].strip()} v {participants[1].split('<')[0].strip()}"
            competition = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "breadcrumb-title"))).get_attribute("innerHTML").strip()
            
        except Exception as e:
            try:
                event_info = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "event-info")))
                event_string = event_info[1].get_attribute("innerHTML")
                competition = event_info[0].get_attribute("innerHTML").strip()            
            except Exception as e:
                raise Exception(f"Could not get event info: {e}")
                
        return event_string, competition


    def get_available_markets(self, event_model):
        # with driver in event page
        market_names = []
        market_tabs_menu = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'option-group-tabs')]")))
        market_tabs = [el.find_element_by_tag_name("span") for el in market_tabs_menu.find_elements_by_xpath(".//li[contains(@class, 'tab-bar-item')]")]  
        
        market_groups_html = []

        for mt in market_tabs[1:]:
            if "build a bet" in mt.get_attribute("innerHTML").lower():
                continue
            # press market tab
            try:
                mt.click()
            except Exception as e:
                try:
                    print(f"Error clicking market tab: {e} - Recharging tabs...")
                    tab_index = market_tabs.index(mt)
                    mt = [el.find_element_by_tag_name("span") for el in market_tabs_menu.find_elements_by_xpath(".//li[contains(@class, 'tab-bar-item')]")][tab_index]
                except Exception as e:
                    raise Exception(f"Error clicking market tab: {e}")

            # get available market groups
            market_groups_html += [BeautifulSoup(mg.get_attribute("innerHTML"), "html.parser") for mg in WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'option-panel')]")))]
            
        for mg in market_groups_html:
            try:
                market_data = self.scrape_market_group(mg)  # market_data: {"market":"Double Chance", "options":[]}
                event_model["markets"].append(market_data)
            except Exception as e:
                print(f"Error scraping market group: {e}")

        return event_model



    def scrape_market_group(self, mg):
        # mg: BeautifulSoup instance
        to_return = {
            "market":"", 
            "options":[]
        }
        
        try:
            to_return["market"] = mg.find("div", {"class":"option-group-name-info-name"}).text
        except Exception as e:
            raise Exception(f"Error getting market name: {e}")
        
        options = mg.findAll("div", {"class":"option-indicator"})
        
        for op in options:
            try:
                selection = op.find("div", {"class":"name"}).text
                odds = op.find("div", {"class":"value"}).text
                to_return["options"].append((selection, odds))
            except Exception as e:
                # raise Exception(f"Error scraping option in market {to_return["market"]}")
                # print(f"Error scraping option in market {to_return["market"]}")
                continue
            
        return to_return






    



if __name__ == "__main__":
    
    event_odder = EventOdder()
    
    event_model = event_odder.scrape_event_information("https://sports.bwin.es/en/sports/events/pedro-cachin-arg-juan-pablo-ficovich-arg-12352843")
    print(event_model)
    input("Done.")