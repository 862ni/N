import os
import re
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
raise RuntimeError(“Missing BOT_TOKEN in Render environment variables”)

logging.basicConfig(level=logging.INFO)

user_states = {}

def make_keyboard():
return InlineKeyboardMarkup([
[InlineKeyboardButton(“🔎 فحص اليوزر”, callback_data=“check”)],
[InlineKeyboardButton(“📝 اختيار يوزر جديد”, callback_data=“change”)],
[InlineKeyboardButton(“ℹ️ معلومات”, callback_data=“info”)],
])

def valid_username(username):
username = username.lstrip(”@”)

if not 1 <= len(username) <= 24:
    return False
if not re.fullmatch(r"[A-Za-z0-9._]+", username):
    return False
if username.endswith("."):
    return False
return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“أهلًا بك في بوت اليوزرات 👋\n\n”
“اختر الخدمة المطلوبة من الأزرار أدناه.\n\n”
“ملاحظة: هذا البوت يفحص صيغة اليوزر فقط، “
“ولا يغيّر اليوزر داخل تيك توك.”,
reply_markup=make_keyboard()
)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

user_id = query.from_user.id
if query.data == "check":
    user_states[user_id] = "check"
    await query.message.reply_text(
        "🔎 أرسل اليوزر لفحص صيغته.\n"
        "مثال: my_username"
    )
elif query.data == "change":
    user_states[user_id] = "change"
    await query.message.reply_text(
        "📝 أرسل اليوزر الذي تريد استخدامه.\n"
        "مثال: new_username"
    )
elif query.data == "info":
    await query.message.reply_text(
        "ℹ️ معلومات البوت\n\n"
        "• فحص صيغة اسم المستخدم.\n"
        "• استقبال يوزر مقترح.\n"
        "• لا يحتاج توكن تيك توك.\n"
        "• لا يفحص توفر اليوزر فعليًا.\n"
        "• لا يغيّر اليوزر تلقائيًا."
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
state = user_states.get(user_id)

if state is None:
    await update.message.reply_text("أرسل /start لبدء الاستخدام.")
    return
username = update.message.text.strip().lstrip("@")
if not valid_username(username):
    await update.message.reply_text(
        "❌ صيغة اليوزر غير صحيحة.\n"
        "استخدم الحروف الإنجليزية والأرقام والنقطة "
        "والشرطة السفلية، بحد أقصى 24 حرفًا."
    )
    return
if state == "check":
    message = (
        "✅ صيغة اليوزر صحيحة.\n"
        "اليوزر: @" + username + "\n\n"
        "هذا لا يؤكد أن اليوزر متاح."
    )
else:
    message = (
        "📝 اليوزر المطلوب: @" + username + "\n\n"
        "لم يتم تغيير اليوزر في تيك توك. "
        "يمكنك تغييره من إعدادات الملف الشخصي "
        "في تطبيق تيك توك الرسمي."
    )
user_states.pop(user_id, None)
await update.message.reply_text(message, reply_markup=make_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_states.pop(update.effective_user.id, None)

await update.message.reply_text(
    "تم إلغاء العملية.",
    reply_markup=make_keyboard()
)

def main():
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
print("Bot started successfully")
app.run_polling()

if name == “main”:
main()
