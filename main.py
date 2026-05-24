import os
import requests
import urllib.parse
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Apne channel ka username yahan '@' ke saath daalein
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', '@YourChannelUsername')

async def is_user_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """User ne channel join kiya hai ya nahi check karne ke liye function"""
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['left', 'kicked']:
            return False
        return True
    except BadRequest:
        print(f"Error: Bot channel {CHANNEL_USERNAME} ko access nahi kar pa raha hai.")
        return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_user_subscribed(update, context):
        await update.message.reply_text('Hello! Main aapki AI GF bot hoon. Mujhse baat karo. 💕')
    else:
        await update.message.reply_text(
            f"⚠️ **Aapko pehle humare channel ko join karna hoga!**\n\n"
            f"Join karein: {CHANNEL_USERNAME}\n\n"
            f"Join karne ke baad dobara /start dabayein."
        )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_subscribed(update, context):
        await update.message.reply_text(
            f"❌ **Aapne lagta hai channel leave kar diya hai!**\n\n"
            f"Aage baat karne ke liye fir se join karein: {CHANNEL_USERNAME}"
        )
        return

    user_message = update.message.text
    safe_message = urllib.parse.quote(user_message)
    api_url = f"https://ukrainexinfo.42web.io/gf-api.php?key=Tushar7demo&message={safe_message}"
    
    # 1. Fake Browser Headers banayein taaki 42web block na kare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 2. Request mein headers pass karein
        res = requests.get(api_url, headers=headers)
        
        # Logs ke liye print lagaya hai taaki Railway dashboard par response dikhe
        print(f"API Status Code: {res.status_code}")
        
        response = res.json()
        reply_message = response.get("reply", "Kuch error aa gaya hai 🥺")
        await update.message.reply_text(reply_message)
        
    except Exception as e:
        # Agar fir bhi koi dikkat aaye, toh asli wajah Railway logs me print hogi
        print(f"Error details: {e}")
        await update.message.reply_text("Abhi main thoda busy hoon, baad mein baat karte hain! 😇")

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable nahi mila!")
        exit(1)
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    print("Bot is running...")
    app.run_polling()
        
