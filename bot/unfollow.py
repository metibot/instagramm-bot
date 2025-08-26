import time, logging
from selenium.webdriver.common.by import By
from bot.db import get_db

logger = logging.getLogger(__name__)

def unfollow_nonfollowers(driver):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, followed_at FROM followings")
    rows = cur.fetchall()
    now = time.time()

    for user_id, followed_at in rows:
        try:
            followed_ts = time.mktime(time.strptime(followed_at, "%Y-%m-%d %H:%M:%S"))
            if now - followed_ts < 12 * 3600:  # 12 hours
                continue
            driver.get(f"https://instagram.com/{user_id}")
            time.sleep(4)
            try:
                unfollow_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Following')]")
                unfollow_btn.click()
                time.sleep(2)
                confirm = driver.find_element(By.XPATH, "//button[contains(text(),'Unfollow')]")
                confirm.click()
                cur.execute("DELETE FROM followings WHERE user_id=?", (user_id,))
                conn.commit()
                logger.info(f"Unfollowed {user_id} after 12h with no followback")
            except Exception:
                logger.info(f"{user_id} already unfollowed or private.")
        except Exception as e:
            logger.error(f"Error checking unfollow for {user_id}: {e}")

    conn.close()
