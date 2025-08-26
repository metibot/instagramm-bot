import time, logging
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def scrape_followers(driver, target_user):
    users = []
    driver.get(f"https://instagram.com/{target_user}")
    time.sleep(3)
    try:
        followers_link = driver.find_element(By.PARTIAL_LINK_TEXT, "followers")
        followers_link.click()
        time.sleep(3)
        dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
        for _ in range(5):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
            time.sleep(2)
        elems = dialog.find_elements(By.TAG_NAME, "a")
        users = [e.get_attribute("href").split("/")[-2] for e in elems if e.get_attribute("href") and "instagram.com" in e.get_attribute("href")]
    except Exception as e:
        logger.error(f"Error scraping followers of {target_user}: {e}")
    return list(set(users))

def scrape_hashtag_posts(driver, hashtag):
    users = []
    driver.get(f"https://www.instagram.com/explore/tags/{hashtag.strip('#')}/")
    time.sleep(4)
    try:
        posts = driver.find_elements(By.XPATH, "//a[contains(@href,'/p/')]")
        for post in posts[:10]:
            post.click()
            time.sleep(2)
            try:
                user_elem = driver.find_element(By.XPATH, "//a[contains(@href,'/')]")
                user_id = user_elem.get_attribute("href").split("/")[-2]
                if user_id not in users:
                    users.append(user_id)
            except Exception:
                continue
            driver.find_element(By.XPATH, "//button[contains(text(),'Close')]").click()
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error scraping hashtag {hashtag}: {e}")
    return users
