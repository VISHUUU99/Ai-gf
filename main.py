import os
import json
import urllib.parse
from playwright.async_api import async_playwright
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', '@YourChannelUsername')

async def is_user_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """User ne channel join kiya hai ya nahi check karne ke liye"""
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
    
    # Playwright ka use karke anti-bot ko browser se bypass karenge
    async with async_playwright() as p:
        try:
            # Headless browser open karna (bina screen ke)
            browser = await p.chromium.launch(headless=True)
            
            # Real user agent set karna
            context_page = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context_page.new_page()
            
            # API page par jana aur load hone ka wait karna
            await page.goto(api_url, wait_until="networkidle")
            
            # Pure screen par jo raw text (JSON) aaya hai use nikalna
            content = await page.locator("body").inner_text()
            await browser.close()
            
            # Text ko wapas Python dictionary (JSON) mein convert karna
            response = json.loads(content)
            reply_message = response.get("reply", "Hmm... main samajh nahi payi 🥺")
            await update.message.reply_text(reply_message)
            
        except Exception as e:
            print(f"Playwright/API Error: {e}")
            await update.message.reply_text("Abhi main thoda busy hoon, baad mein baat karte hain! 😇")

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable nahi mila!")
        exit(1)
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    print("Bot is running with Playwright bypass...")
    app.run_polling()
            
