import time, random, logging
from selenium.webdriver.common.by import By
from bot.db import get_db

logger = logging.getLogger(__name__)

def human_delay(a=2, b=5):
    time.sleep(random.uniform(a, b))

def like_post(driver, post_url, user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM interactions WHERE post_id=? AND action='like'", (post_url,))
    if cur.fetchone():
        conn.close()
        logger.info(f"Already liked {post_url}")
        return False

    driver.get(post_url)
    human_delay(3, 6)
    try:
        like_button = driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Like']")
        like_button.click()
        human_delay()
        cur.execute("INSERT INTO interactions (user_id, post_id, action) VALUES (?, ?, 'like')", (user_id, post_url))
        conn.commit()
        logger.info(f"Liked post {post_url} of user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error liking post {post_url}: {e}")
    finally:
        conn.close()
    return False

def follow_user(driver, user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM interactions WHERE user_id=? AND action='follow'", (user_id,))
    if cur.fetchone():
        conn.close()
        logger.info(f"Already followed {user_id}")
        return False

    driver.get(f"https://instagram.com/{user_id}")
    human_delay(3, 6)
    try:
        follow_button = driver.find_element(By.XPATH, "//button[contains(text(),'Follow')]")
        follow_button.click()
        human_delay()
        cur.execute("INSERT INTO interactions (user_id, action) VALUES (?, 'follow')", (user_id,))
        cur.execute("INSERT OR IGNORE INTO followings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        logger.info(f"Followed {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error following {user_id}: {e}")
    finally:
        conn.close()
    return False

def comment_post(driver, post_url, user_id, comment_text):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM interactions WHERE post_id=? AND action='comment'", (post_url,))
    if cur.fetchone():
        conn.close()
        logger.info(f"Already commented {post_url}")
        return False

    driver.get(post_url)
    human_delay(3, 6)
    try:
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        textarea.click()
        human_delay()
        textarea.send_keys(comment_text)
        human_delay()
        post_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Post')]")
        post_btn.click()
        cur.execute("INSERT INTO interactions (user_id, post_id, action) VALUES (?, ?, 'comment')", (user_id, post_url))
        conn.commit()
        logger.info(f"Commented on {post_url} of user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error commenting {post_url}: {e}")
    finally:
        conn.close()
    return False
