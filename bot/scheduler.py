import time, random, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bot.db import init_db
from bot.actions import follow_user, like_post, comment_post
from bot.unfollow import unfollow_nonfollowers
from bot.dm import process_scheduled_dms, schedule_welcome_dm
from bot.reciprocal import check_notifications_and_like_back
from bot.scraper import scrape_followers, scrape_hashtag_posts

import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
TARGET_PAGES = os.getenv("TARGET_PAGES", "").split(",")
TARGET_HASHTAGS = os.getenv("TARGET_HASHTAGS", "").split(",")

def login(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    driver.find_element("name", "username").send_keys(IG_USERNAME)
    driver.find_element("name", "password").send_keys(IG_PASSWORD)
    driver.find_element("xpath", "//button[@type='submit']").click()
    time.sleep(8)

def run_scheduler():
    init_db()

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    login(driver)

    cycle = 0
    while True:
        cycle += 1
        logger.info(f"--- Cycle {cycle} ---")

        # 1. Scrape new users
        candidates = []
        for page in TARGET_PAGES:
            if page.strip():
                candidates += scrape_followers(driver, page.strip("@"))
        for tag in TARGET_HASHTAGS:
            if tag.strip():
                candidates += scrape_hashtag_posts(driver, tag.strip("#"))
        candidates = list(set(candidates))
        random.shuffle(candidates)

        # 2. Follow & like a few users
        for user_id in candidates[:3]:
            if follow_user(driver, user_id):
                schedule_welcome_dm(user_id)
                time.sleep(random.randint(5, 15))
                try:
                    driver.get(f"https://instagram.com/{user_id}")
                    time.sleep(3)
                    posts = driver.find_elements("xpath", "//a[contains(@href,'/p/')]")
                    if posts:
                        like_post(driver, posts[0].get_attribute("href"), user_id)
                except Exception as e:
                    logger.error(f"Error liking {user_id}'s post: {e}")

        # 3. Process scheduled DMs
        process_scheduled_dms(driver)

        # 4. Reciprocal like
        check_notifications_and_like_back(driver)

        # 5. Unfollow non-followers
        unfollow_nonfollowers(driver)

        # Wait random time before next cycle
        sleep_time = random.randint(300, 600)
        logger.info(f"Sleeping {sleep_time} sec before next cycle...")
        time.sleep(sleep_time)
