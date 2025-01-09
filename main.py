import requests
import re
from user_agent import generate_user_agent
import telebot

# متغيرات البيئة
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_USERNAME = os.getenv("GROUP_USERNAME")

bot = telebot.TeleBot(BOT_TOKEN)

WELCOME_MESSAGE = """\
*WELCOME TO BOT FREE FIRE MADE BY CODEX TEAM*
---------------------------------------------------------------------------
"""
FEATURES_MESSAGE = """\
*Choose one of the following features:*
[1] - Get the player's pet animal 🐾  
[2] - Get the account age 📅  
[3] - Send visitors 👥  
[4] - Send the bot 🤖  
[5] - Visitors (Lag) 🔄  
[6] - Get degree of pride 🏆  
[7] - Check if the player is in the blacklist 🚫  
[8] - Check if the player is under protection 🛡️  
[9] - Block ID in write message✋  
[10] - Get the player's bio 📝  
"""
APIS = {
    "1": "https://fadai-boma-bot-vtwo-pro.vercel.app/pet",
    "2": "https://fadai-boma-bot-vtwo-pro.vercel.app/log",
    "3": "https://fadai-boma-bot-vtwo-pro.vercel.app/increase_visitors",
    "4": "https://fadai-boma-bot-vtwo-pro.vercel.app/send_bot",
    "5": "https://fadai-boma-bot-vtwo-pro.vercel.app/visit_max",
    "6": "https://fadai-boma-bot-vtwo-pro.vercel.app/fakhr",
    "7": "https://fadai-boma-bot-vtwo-pro.vercel.app/acc",
    "8": "https://fadai-boma-bot-vtwo-pro.vercel.app/acc1",
    "9": "https://fadai-boma-bot-vtwo-pro.vercel.app/ban",
    "10": "https://fadai-boma-bot-vtwo-pro.vercel.app/bio",
}
HEADERS = {
    'authority': 'fadai-boma-bot-vtwo-pro.vercel.app',
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://fadai-boma-bot-vtwo-pro.vercel.app',
    'referer': 'https://fadai-boma-bot-vtwo-pro.vercel.app/home',
    'user-agent': generate_user_agent(),
}

# دالة للتحقق من انضمام المستخدم إلى المجموعة
def is_user_in_group(user_id):
    try:
        member = bot.get_chat_member(chat_id=GROUP_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    if is_user_in_group(user_id):
        bot.reply_to(message, WELCOME_MESSAGE + FEATURES_MESSAGE, parse_mode="Markdown")
    else:
        bot.reply_to(
            message,
            f"❌ *Access Denied*: Please join the group {GROUP_USERNAME} to use this bot.",
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda msg: msg.text.isdigit() and msg.text in APIS.keys())
def handle_feature_choice(message):
    user_id = message.from_user.id
    if not is_user_in_group(user_id):
        bot.reply_to(
            message,
            f"❌ *Access Denied*: Please join the group {GROUP_USERNAME} to use this bot.",
            parse_mode="Markdown"
        )
        return
    
    feature = message.text
    api_url = APIS[feature]
    bot.reply_to(message, f"🚀 *Feature {feature}*: Please enter your UID:", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_feature, feature, api_url)

def process_feature(message, feature, api_url):
    uid = message.text
    data = {'text': uid}
    response = requests.post(api_url, headers=HEADERS, json=data)

    if response.status_code == 200:
        try:
            msg = response.json().get("message", "").encode('utf-8').decode('unicode_escape')
            if feature == "1":
                result = re.search(r"<br>(.*?)\n", msg)
                pet_name = result.group(1).strip() if result else "No data available."
                bot.reply_to(message, f"🐾 *Player's Pet Animal*: {pet_name}", parse_mode="Markdown")
            elif feature == "2":
                result = re.search(r"\n(.*?)\n", msg)
                account_age = result.group(1).strip() if result else "No data available."
                bot.reply_to(message, f"📅 *Account Age*: {account_age}", parse_mode="Markdown")
            elif feature == "3":
                bot.reply_to(message, f"👥 *Visitor count increased for UID*: {uid}", parse_mode="Markdown")
            elif feature == "4":
                bot.reply_to(message, f"🤖 *Bot successfully sent to UID*: {uid}", parse_mode="Markdown")
            elif feature == "5":
                bot.reply_to(message, f"🔄 *Lag created for UID*: {uid}", parse_mode="Markdown")
            elif feature == "6":
                result = re.search(r"\n(.*?)\n", msg)
                pride = result.group(1).strip() if result else "No data available."
                bot.reply_to(message, f"🏆 *Pride*: {pride}", parse_mode="Markdown")
            elif feature == "7":
                result = re.search(r"<br>(.*?)<br>", msg)
                blacklist_status = result.group(1).strip() if result else "No data available."
                bot.reply_to(message, f"🚫 *Blacklist status*: {blacklist_status}", parse_mode="Markdown")
            elif feature == "8":
                result = re.search(r"<br>(.*?)<br>", msg)
                protection_status = result.group(1).strip() if result else "No data available."
                bot.reply_to(message, f"🛡️ *Protection status*: {protection_status}", parse_mode="Markdown")
            elif feature == "9":
                bot.reply_to(message, f"✋ *UID blocked*: {uid}", parse_mode="Markdown")
            elif feature == "10":
                result = re.search(r"\n(.*?)\n", msg)
                bio = result.group(1).strip() if result else "No data available."
                bot.reply_to(message, f"📝 *Bio*: {bio}", parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ *Unknown feature error!*", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ *Error processing response:* {e}", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ *Failed to connect to the server: {response.status_code}*", parse_mode="Markdown")

bot.polling()
