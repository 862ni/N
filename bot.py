import os
import re
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
Application,
CommandHandler,
CallbackQueryHandler,
MessageHandler,
ContextTypes,
filters,
)

logging.basicConfig(
format=”%(asctime)s - %(name)s - %(levelname)s - %(message)s”,
level=logging.INFO,
)

logger = logging.getLogger(name)

BOT_TOKEN = os.environ.get(“BOT_TOKEN”, “”)

if not BOT_TOKEN:
raise RuntimeError(
“BOT_TOKEN is missing. Add it in Render Environment Variables.”
)

Store temporary interaction state for each Telegram user.

user_states = {}

def main_keyboard():
keyboard = [
[
InlineKeyboardButton(
“🔑 فحص صيغة اليوزر”,
callback_data=“check”,
)
],
[
InlineKeyboardButton(
“📝 إدخال يوزر جديد”,
callback_data=“username”,
)
],
[
InlineKeyboardButton(
“ℹ️ معلومات البوت”,
callback_data=“info”,
)
],
]

return InlineKeyboardMarkup(keyboard)

def valid_username(username):
if username.startswith(”@”):
username = username[1:]

if not 1 <= len(username) <= 24:
    return False
if not re.fullmatch(r"[A-Za-z0-9._]+", username):
    return False
if username.endswith("."):
    return False
return True

async def start(
update: Update,
context: ContextTypes.DEFAULT_TYPE,
):
await update.message.reply_text(
“أهلًا بك في بوت إدارة يوزر تيك توك 👋\n\n”
“اختر الخدمة التي تريدها من القائمة:\n\n”
“🔑 فحص صيغة اسم المستخدم\n”
“📝 إدخال اسم مستخدم جديد\n\n”
“⚠️ هذا البوت لا يغيّر اليوزر فعليًا، “
“ولا يحتاج إلى توكن حساب تيك توك.”,
reply_markup=main_keyboard(),
)

async def handle_buttons(
update: Update,
context: ContextTypes.DEFAULT_TYPE,
):
query = update.callback_query
await query.answer()

user_id = query.from_user.id
if query.data == "check":
    user_states[user_id] = "check"
    await query.message.reply_text(
        "🔎 أرسل اسم المستخدم لفحص صيغته.\n\n"
        "مثال: my_username\n\n"
        "لا ترسل كلمة المرور أو توكن حسابك."
    )
elif query.data == "username":
    user_states[user_id] = "username"
    await query.message.reply_text(
        "📝 أرسل اليوزر الجديد الذي تريده.\n\n"
        "مثال: my_new_username\n\n"
        "ملاحظة: سيتم فحص الصيغة فقط، "
        "ولن يتغير اليوزر داخل تيك توك."
    )
elif query.data == "info":
    await query.message.reply_text(
        "ℹ️ معلومات البوت\n\n"
        "• فحص صيغة اسم المستخدم.\n"
        "• استقبال اسم مستخدم مقترح.\n"
        "• لا يستقبل توكن تيك توك.\n"
        "• لا يتحقق من توفر اليوزر.\n"
        "• لا يغيّر اليوزر تلقائيًا.\n\n"
        "لتغيير اليوزر فعليًا، استخدم تطبيق "
        "تيك توك الرسمي."
    )

async def handle_text(
update: Update,
context: ContextTypes.DEFAULT_TYPE,
):
user_id = update.effective_user.id
state = user_states.get(user_id)

if state is None:
    await update.message.reply_text(
        "اكتب /start لعرض قائمة البوت."
    )
    return
username = update.message.text.strip()
if username.startswith("@"):
    username = username[1:]
if not valid_username(username):
    await update.message.reply_text(
        "❌ صيغة اليوزر غير صحيحة.\n\n"
        "استخدم الأحرف الإنجليزية والأرقام "
        "والنقطة والشرطة السفلية، "
        "وبحد أقصى 24 حرفًا.\n\n"
        "حاول مرة أخرى."
    )
    return
if state == "check":
    await update.message.reply_text(
        f"✅ صيغة اليوزر @{username} صحيحة.\n\n"
        "⚠️ هذا لا يعني أن اليوزر متاح؛ "
        "البوت لا يفحص التوفر الفعلي."
    )
elif state == "username":
    await update.message.reply_text(
        f"📝 اليوزر الذي اخترته: @{username}\n\n"
        "لم يتم تغيير اليوزر في تيك توك.\n"
        "يمكنك تغييره من ملفك الشخصي "
        "داخل تطبيق تيك توك الرسمي."
    )
user_states.pop(user_id, None)
await update.message.reply_text(
    "اختر خدمة أخرى:",
    reply_markup=main_keyboard(),
)

async def cancel(
update: Update,
context: ContextTypes.DEFAULT_TYPE,
):
user_states.pop(update.effective_user.id, None)

await update.message.reply_text(
    "تم إلغاء العملية. ✅",
    reply_markup=main_keyboard(),
)

def main():
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(
    CallbackQueryHandler(handle_buttons)
)
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text,
    )
)
logger.info("Telegram bot is starting...")
app.run_polling()

if name == “main”:
main()
