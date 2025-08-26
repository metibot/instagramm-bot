import time
import random
import logging

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

def human_delay(min_sec=2, max_sec=5):
    """ایجاد تأخیر تصادفی برای شبیه‌سازی رفتار انسانی"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay
