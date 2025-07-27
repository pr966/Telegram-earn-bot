import telebot
from telebot import types
import sqlite3
import time
import datetime
import logging

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7784511499:AAFD3NxMnr_0Fql1JHhTNvDd_0_CwSXdR0U'
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 6656908267
CHANNEL_USERNAME = "@adstoearnhere"

# Ad links dictionary
ad_links = {
    "Ad 1": "https://www.profitableratecpm.com/c18dzv85?key=7ef3008c70d644c24061e6af08800420/ad1",
    "Ad 2": "https://www.profitableratecpm.com/e7mycn4sya?key=5fc561a5cb39dce85552f7f01de5a0b7/ad2",
    "Ad 3": "https://www.profitableratecpm.com/n07dmhhu?key=34975be2aee853d77f2f5662c07778cb/ad3",
    "Ad 4": "https://www.profitableratecpm.com/ycp47wigbu?key=e6705cee625626ea2f625daf7656a32b/ad4",
    "Ad 5": "https://www.profitableratecpm.com/ajag6zq3?key=b119aafe0d045e004efcad2e525b7205/ad5",
    "Ad 6": "https://www.profitableratecpm.com/a5wieq0p?key=2aa3fc0d3d520192bfb60594009e75da/ad6",
    "Ad 7": "https://www.profitableratecpm.com/c18dzv85?key=7ef3008c70d644c24061e6af08800420/ad7",
    "Ad 8": "https://www.profitableratecpm.com/s3sdguahg?key=fadf94afc809023c999e0b775709bdd3/ad8",
    "Ad 9": "https://www.profitableratecpm.com/nin40jwue?key=3fae381386ad0da42e1346cb9fb5ccac/ad9",
    "Ad 10": "https://www.profitableratecpm.com/st1g62y0s?key=244c4ed87518d23f1208efd87838d12e/ad10",
}

# SQLite setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        balance INTEGER, 
        last_ad_time INTEGER, 
        referrals INTEGER, 
        referred_by INTEGER
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS withdraws (
        user_id INTEGER, 
        method TEXT, 
        number TEXT, 
        amount INTEGER, 
        status TEXT
    )
""")
conn.commit()

user_screenshot_waiting = {}

def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status not in ['left', 'kicked']
    except:
        return False

def check_channel_join(func):
    def wrapper(message):
        if not is_joined(message.chat.id):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("চ্যানেলে জয়েন করুন", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"))
            bot.send_message(message.chat.id, "🚫 বট ব্যবহার করতে হলে আমাদের চ্যানেলে অবশ্যই জয়েন হতে হবে। জয়েন হওয়ার পর মেনু বাটন থেকে আবার Start বাটনে ক্লিক করুন😊", reply_markup=markup)
            return
        return func(message)
    return wrapper

def add_user(user_id, referred_by=None):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user_id, 0, 0, 0, referred_by))
        if referred_by:
            cursor.execute("UPDATE users SET referrals = referrals + 1, balance = balance + 50 WHERE id=?", (referred_by,))
        conn.commit()

@bot.message_handler(commands=['start'])
@check_channel_join
def start(message):
    user_id = message.chat.id
    args = message.text.split()
    referred_by = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
    add_user(user_id, referred_by)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👁️ Watch Ad", "💰 Balance")
    markup.add("📤 Withdraw", "👥 Referral")
    if user_id == ADMIN_ID:
        markup.add("👨‍💻 Admin Panel", "📢 Broadcast")
    bot.send_message(user_id, "👋 Earn From Ads Bot এ আপনাকে স্বাগতম! নিছের দেওয়া মেনু থেকে Watch Ad বাটনে ক্লিক করে আজই ইনকাম করা শুরু করে দিন😊", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "👁️ Watch Ad")
@check_channel_join
def watch_ad(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for name in ad_links:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"ad_{name}"))
    bot.send_message(message.chat.id, "👇 নিচের যেকোনো একটি বিজ্ঞাপন লিংকে ক্লিক করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ad_"))
def handle_ad(call):
    ad_name = call.data.split("_", 1)[1]
    user_id = call.message.chat.id
    link = ad_links[ad_name]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 লিংকে যান", url=link))
    bot.send_message(user_id, f"✅ {ad_name} লিংকে ক্লিক করুন এবং ৬০ সেকেন্ড নিয়ে যাওয়া লিংকে অপেক্ষা করুন। তারপর ৬০ সেকেন্ড পর কনফার্ম করুন।", reply_markup=markup)
    time.sleep(65)
    confirm = types.InlineKeyboardMarkup()
    confirm.add(types.InlineKeyboardButton("✅ হ্যাঁ আমি লিংকে ক্লিক করেছি", callback_data=f"confirm_{ad_name}"))
    bot.send_message(user_id, "আপনি কী লিংকে ক্লিক করেছেন?", reply_markup=confirm)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_ad(call):
    user_id = call.message.chat.id
    cursor.execute("UPDATE users SET balance = balance + 10 WHERE id=?", (user_id,))
    conn.commit()
    bot.send_message(user_id, "🎉 অভিনন্দন! আপনার এডস দেখা সফল হয়েছে✅।আপনি ১০ কয়েন পেয়েছেন🪙। আরো এডস দেখতে নিচের মেনু বাটন থেকে Watch Ad🎥 বাটনে ক্লিক করুন😊।")

@bot.message_handler(func=lambda m: m.text == "💰 Balance")
@check_channel_join
def balance(message):
    cursor.execute("SELECT balance FROM users WHERE id=?", (message.chat.id,))
    bal = cursor.fetchone()[0]
    bot.send_message(message.chat.id, f"💰 আপনার ব্যালেন্স: {bal} কয়েন")

@bot.message_handler(func=lambda m: m.text == "👥 Referral")
@check_channel_join
def referral(message):
    cursor.execute("SELECT referrals FROM users WHERE id=?", (message.chat.id,))
    total = cursor.fetchone()[0]
    link = f"https://t.me/{bot.get_me().username}?start={message.chat.id}"
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিংক: {link}\n👥 মোট রেফার: {total}")

@bot.message_handler(func=lambda m: m.text == "📤 Withdraw")
@check_channel_join
def withdraw(message):
    cursor.execute("SELECT balance, referrals FROM users WHERE id=?", (message.chat.id,))
    bal, refs = cursor.fetchone()
    if bal < 1000:
        return bot.send_message(message.chat.id, "❌ উইথড্র করতে ১০০০ কয়েন লাগবে।")
    if refs < 10:
        return bot.send_message(message.chat.id, "❌ অন্তত ১০ রেফার করতে হবে।")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("bKash", callback_data="pay_bkash"))
    markup.add(types.InlineKeyboardButton("Nagad", callback_data="pay_nagad"))
    bot.send_message(message.chat.id, "📱 পেমেন্ট মেথড নির্বাচন করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def process_payment_method(call):
    method = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, f"📞 {method} নম্বর দিন (১১ ডিজিট):")
    bot.register_next_step_handler(msg, lambda m: ask_amount(m, method))

def ask_amount(message, method):
    number = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("৫০৳ (1000 Coins)", callback_data=f"withdraw_{method}_{number}_50"))
    bot.send_message(message.chat.id, "পরিমাণ নির্বাচন করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("withdraw_"))
def confirm_withdraw(call):
    _, method, number, taka = call.data.split("_")
    user_id = call.message.chat.id
    coins = int(taka) * 20
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    if cursor.fetchone()[0] < coins:
        return bot.send_message(user_id, "❌ যথেষ্ট কয়েন নেই।")
    cursor.execute("UPDATE users SET balance = balance - ? WHERE id=?", (coins, user_id))
    cursor.execute("INSERT INTO withdraws VALUES (?, ?, ?, ?, 'Pending')", (user_id, method, number, int(taka)))
    conn.commit()
    bot.send_message(user_id, f"✅ {taka}৳ অনুরোধ গ্রহণ করা হয়েছে।")

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Payment Done", callback_data=f"done_{user_id}"),
        types.InlineKeyboardButton("❌ Payment Rejected", callback_data=f"reject_{user_id}")
    )
    bot.send_message(ADMIN_ID, f"🔔 ইউজার {user_id} {taka}৳ চাচ্ছে:\nMethod: {method}\nNumber: {number}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def payment_done(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "✅ আপনার পেমেন্ট দেওয়া হয়েছে!\n📸 পেমেন্ট স্ক্রিনশট ও রিভিউ দিন:")
    user_screenshot_waiting[user_id] = True

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_withdraw(call):
    user_id = int(call.data.split("_")[1])
    msg = bot.send_message(ADMIN_ID, "❗ রিজেক্টের কারণ লিখুন:")
    bot.register_next_step_handler(msg, lambda m: bot.send_message(user_id, f"❌ পেমেন্ট বাতিল।\nকারণ: {m.text}"))

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if user_screenshot_waiting.get(message.chat.id):
        caption = message.caption or "No caption"
        bot.send_photo(CHANNEL_USERNAME, message.photo[-1].file_id, caption=f"📷 ইউজার {message.chat.id}: {caption}")
        bot.send_message(message.chat.id, "✅ আপনার রিভিউ ও ছবি চ্যানেলে পাঠানো হয়েছে। ধন্যবাদ!")
        user_screenshot_waiting.pop(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Admin Panel")
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()
    msg = f"👥 মোট ইউজার: {total}\n\n"
    for user in all_users:
        uid, _, _, refs, ref_by = user
        msg += f"👤 {uid} | রেফার: {refs} | রেফার্ড বাই: {ref_by}\n"
    bot.send_message(ADMIN_ID, msg)

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def broadcast_prompt(message):
    if message.chat.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "✉️ বার্তা লিখুন:")
    bot.register_next_step_handler(msg, broadcast_send)

def broadcast_send(message):
    cursor.execute("SELECT id FROM users")
    for (uid,) in cursor.fetchall():
        try:
            bot.send_message(uid, f"📢 বিজ্ঞপ্তি/নোটিশ/ঘোষণা: {message.text}")
        except:
            continue
    bot.send_message(ADMIN_ID, "✅ বার্তা পাঠানো হয়েছে।")

# ✅ Render-ready infinite polling loop
while True:
    try:
        logger.info("বট চালু হচ্ছে...")
        bot.polling(none_stop=True, interval=0, timeout=10)
    except Exception as e:
        logger.error(f"ত্রুটি! বট বন্ধ হয়েছে: {e}")
        logger.info("০৫ সেকেন্ড পর আবার চালু হবে...")
        time.sleep(5)