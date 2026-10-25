import os
import re
import logging
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
Application,
CommandHandler,
CallbackQueryHandler,
MessageHandler,
ContextTypes,
filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

BOT_TOKEN = os.environ.get(“BOT_TOKEN”, “”)

if not BOT_TOKEN:
raise RuntimeError(“Set BOT_TOKEN in Render environment variables.”)

Temporary per-user state. Never log or persist account tokens.

user_states = {}

def main_keyboard():
return InlineKeyboardMarkup([
[InlineKeyboardButton(“🔑 فحص التوكن”, callback_data=“check”)],
[InlineKeyboardButton(“📝 تغيير اليوزر”, callback_data=“username”)],
[InlineKeyboardButton(“ℹ️ معلومات”, callback_data=“info”)],
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“أهلًا بك في بوت إدارة يوزر تيك توك 👋\n\n”
“اختر الخدمة من القائمة أدناه:\n\n”
“⚠️ لا ترسل توكن حسابك أو كلمة المرور. “
“هذا البوت لا يغيّر اليوزر فعليًا؛ يلزم تكامل رسمي مدعوم من تيك توك.”,
reply_markup=main_keyboard(),
)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

uid = query.from_user.id
if query.data == "check":
    user_states[uid] = "check"
    await query.message.reply_text(
        "أرسل اسم مستخدم تيك توك (@username) لفحص صيغته.\n"
        "لا ترسل توكن الحساب."
    )
elif query.data == "username":
    user_states[uid] = "username"
    await query.message.reply_text(
        "أرسل اليوزر الجديد الذي تريده، بدون كلمة مرور أو توكن.\n"
        "مثال: my_username"
    )
elif query.data == "info":
    await query.message.reply_text(
        "البوت يوفر فحصًا محليًا لصيغة اسم المستخدم فقط.\n"
        "لا يتحقق من توفر اليوزر ولا يغيّره داخل تيك توك.\n"
        "يمكنك تغيير اليوزر من تطبيق تيك توك الرسمي."
    )

async def handle_message(
update: Update, context: ContextTypes.DEFAULT_TYPE
):
uid = update.effective_user.id
state = user_states.get(uid)
value = update.message.text.strip()

if state not in ("check", "username"):
    await update.message.reply_text(
        "استخدم /start لعرض القائمة."
    )
    return
username = value.removeprefix("@")
# TikTok usernames generally allow letters, numbers,
# underscores and periods, with a 24-character limit.
valid = (
    1 <= len(username) <= 24
    and re.fullmatch(r"[A-Za-z0-9._]+", username) is not None
    and not username.endswith(".")
)
if not valid:
    await update.message.reply_text(
        "❌ صيغة اليوزر غير صحيحة.\n"
        "استخدم الأحرف الإنجليزية والأرقام والنقطة "
        "والشرطة السفلية، وبحد أقصى 24 حرفًا."
    )
    return
if state == "check":
    await update.message.reply_text(
        f"✅ صيغة اليوزر @{username} صحيحة.\n"
        "هذا الفحص لا يؤكد أن اليوزر متاح أو مستخدم."
    )
elif state == "username":
    await update.message.reply_text(
        f"📝 اليوزر المطلوب: @{username}\n\n"
        "لم يتم تغيير اليوزر؛ لا توجد واجهة رسمية "
        "مهيأة لتنفيذ التغيير في هذا البوت.\n"
        "يمكنك تغييره من الملف الشخصي في تطبيق تيك توك."
    )
user_states.pop(uid, None)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_states.pop(update.effective_user.id, None)
await update.message.reply_text(
“تم إلغاء العملية.”,
reply_markup=main_keyboard(),
)

async def main():
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)
logger.info("Telegram bot is starting")
await app.initialize()
await app.start()
await app.updater.start_polling()
try:
    await asyncio.Event().wait()
finally:
    await app.updater.stop()
    await app.stop()
    await app.shutdown()

if name == “main”:
asyncio.run(main())
