import random, time, logging
from selenium.webdriver.common.by import By
from bot.db import get_db

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = (
    "سلام عزیزم٫خوش اومدی😍🌹 دوتا هایلایت توی پیج هست ببینشون حتما🔥 👀اول هایلایت “همکاری با ما” رو ببین💰 و بعد هایلایت “ویژگی و آپشن” و ببین👀 هر سوال یا سفارشی داشتی همینجا پیام بزار واسم 🚀🚀👇"
)

def schedule_welcome_dm(user_id):
    conn = get_db()
    cur = conn.cursor()
    delay = random.randint(5, 600)  # 5s to 10m
    scheduled_at = int(time.time()) + delay
    cur.execute("INSERT INTO scheduled_dms (user_id, message, scheduled_at) VALUES (?, ?, ?)",
                (user_id, WELCOME_MESSAGE, scheduled_at))
    conn.commit()
    conn.close()
    logger.info(f"Scheduled DM for {user_id} in {delay} sec")

def process_scheduled_dms(driver):
    conn = get_db()
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("SELECT id, user_id, message FROM scheduled_dms WHERE scheduled_at <= ? AND sent=0", (now,))
    dms = cur.fetchall()
    for dm_id, user_id, msg in dms:
        try:
            driver.get(f"https://instagram.com/{user_id}")
            time.sleep(3)
            msg_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Message')]")
            msg_btn.click()
            time.sleep(2)
            textarea = driver.find_element(By.TAG_NAME, "textarea")
            textarea.send_keys(msg)
            time.sleep(1)
            send_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Send')]")
            send_btn.click()
            cur.execute("UPDATE scheduled_dms SET sent=1 WHERE id=?", (dm_id,))
            conn.commit()
            logger.info(f"Sent DM to {user_id}")
        except Exception as e:
            logger.error(f"Error sending DM to {user_id}: {e}")
    conn.close()
