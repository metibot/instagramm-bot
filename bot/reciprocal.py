import time, logging
from selenium.webdriver.common.by import By
from bot.actions import like_post
from bot.db import get_db

logger = logging.getLogger(__name__)

def check_notifications_and_like_back(driver):
    driver.get("https://www.instagram.com/accounts/activity/")
    time.sleep(5)

    conn = get_db()
    cur = conn.cursor()

    try:
        items = driver.find_elements(By.XPATH, "//a[contains(@href,'/p/')]")
        for item in items[:5]:
            try:
                href = item.get_attribute("href")
                user_elem = item.find_element(By.XPATH, "../../..//a")
                user_id = user_elem.get_attribute("href").split("/")[-2]
                cur.execute("SELECT 1 FROM interactions WHERE user_id=? AND action='reciprocal'", (user_id,))
                if cur.fetchone():
                    continue
                driver.get(f"https://instagram.com/{user_id}")
                time.sleep(3)
                if "This Account is Private" in driver.page_source:
                    continue
                posts = driver.find_elements(By.XPATH, "//a[contains(@href,'/p/')]")
                if posts:
                    latest_post = posts[0].get_attribute("href")
                    if like_post(driver, latest_post, user_id):
                        cur.execute("INSERT INTO interactions (user_id, post_id, action) VALUES (?, ?, 'reciprocal')", (user_id, latest_post))
                        conn.commit()
                        logger.info(f"Reciprocal liked {user_id}'s latest post")
            except Exception as e:
                logger.error(f"Error in reciprocal like: {e}")
    finally:
        conn.close()
