from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from typing import List,Union
from utils import dtime,file
from time import sleep
from tqdm import tqdm
import traceback
import datetime
import requests
import logging
import sys
import os

# Global Variables
# ----------------
DEFAULT_DATE_RANGE = 3
MATCH_CSS = ".mls-o-match-strip.mls-o-match-strip--pre.mls-o-match-strip--hide-promo"
MATCH_DATE_CSS = ".mls-o-match-strip__match-time"     
MATCH_LINK_CSS = ".mls-o-match-strip__matchhub-link"
MATCH_OPPONENT_CSS = ".mls-o-match-strip__club-short-name"
MATCH_TIME_CSS = ".mls-o-match-strip__time"

# Global Configuration
# --------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create handlers
sh = logging.StreamHandler()
fh = logging.FileHandler(f"logs/{dtime.get_today(string=True)[:10]}.log")

# set handler levels
sh.setLevel(logging.DEBUG); fh.setLevel(logging.INFO)

# add formatter to handlers
fmt = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
sh.setFormatter(fmt); fh.setFormatter(fmt)

# add handlers to logger
logger.addHandler(sh); logger.addHandler(fh)

# Public API
# ----------
def set_discord_message_on_events_channel(url:str,message:str) -> None:
    """
    Posts a given `message` on events channel using the webhook associated with given `url`.
    """
    # create a session to make POST request
    with requests.Session() as session:
        session.post(f"{url}",json={"content":message})

def get_driver() -> webdriver.Firefox:
    """
    Returns a Selenium webdriver
    """
    # import dependencies
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    from webdriver_manager.firefox import GeckoDriverManager

    # define an option to make a headless mariennette
    options = Options()
    options.add_argument("-headless")

    return webdriver.Firefox(service=Service(GeckoDriverManager().install(),log_path=os.devnull),options=options)

def get_match_elements(driver:webdriver.Firefox,url:str,match_css:str) -> List[WebElement]:
    """
    Returns a list of links for matches scraped from given URL
    """
    # get the Inter Miami website
    driver.get(url)
    sleep(2)

    # get a list of web elements that contain match info
    matches = WebDriverWait(driver,timeout=5).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,match_css)))
    return matches

def get_match_link(match:WebElement,link_css:str) -> Union[str,None]:
    """
    Returns a list of links for matches scraped from given URL
    """
    try:
        link = match.find_element(By.CSS_SELECTOR,link_css)
        return link.get_attribute("href")
    except:
        return None

def get_match_date(match:WebElement,date_css:str) -> Union[datetime.date,None]:
    """
    Returns a list of dates for matches scraped from given URL
    """
    try:
        date:WebElement = match.find_element(By.CSS_SELECTOR,date_css)
        return datetime.date.fromisoformat(date.text)
    except:
        return None

def get_match_time(match:WebElement,time_css:str) -> Union[str,None]:
    """
    Returns a list of times for matches scraped from given URL
    """
    try:
        time:WebElement = match.find_element(By.CSS_SELECTOR,time_css)
        return time.text
    except:
        return None

# Driver
# ------
if __name__ == "__main__":

    logger.info("--- SCRAPING ---")

    # define the url for the webhook to post on
    webhook_base = os.environ["DISCORD_BASE_URL"]
    webhook_id = os.environ["DISCORD_WEBHOOK_ID_TESTBOT"]
    webhook_token = os.environ["DISCORD_WEBHOOK_TOKEN_TESTBOT"]
    webhook_url = f"{webhook_base}/{webhook_id}/{webhook_token}"

    # get a webdriver
    driver = get_driver()

    # define the URL for the site to scrape
    site = os.environ["SCRAPE_INTER_MIAMI_URL"]

    # get match elements
    matches = get_match_elements(driver,site,MATCH_CSS)

    logger.info(f"Found {len(matches)} matches...")

#    try:
    # iterate over match_elements
    for match in tqdm(matches):

        # get link, time, and date
        m_link = get_match_link(match,MATCH_LINK_CSS)
        m_time = get_match_time(match,MATCH_TIME_CSS)
        m_date = get_match_date(match,MATCH_DATE_CSS)

        print(m_time,m_date)

        if None in [m_link,m_time,m_date]:
            continue

        # check if match date is upcoming
        diff = m_date - datetime.date.today()
        if diff.days >= 0 and diff.days <= DEFAULT_DATE_RANGE:
            
            # render the templated message 
            message = file.get_content_from_template("match.md",match_link=m_link,match_time=m_time,match_date=m_date)

            # send the message on discord
            set_discord_message_on_events_channel(webhook_url,message)

#    except: logger.error(traceback.format_exc()); sys.exit(1)
#    finally: 
    driver.quit()
