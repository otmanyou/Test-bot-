import logging
import marshal
import dis
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, filters
from io import BytesIO
import os

# إعدادات تسجيل الدخول للـ Telegram Bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# إعدادات البوت
BOT_TOKEN = "5175709686:AAEs5-jvaCRmoEK8d0Ix8GUHj2ze3uJ0Abk"
ADMIN_ID = 5164991393  # ايدي المسؤول
YOUTUBE_CHANNEL_URL = "https://youtube.com/@l7aj.1m"  # رابط قناة يوتيوب

# دالة تحقق من الاشتراك في قناة يوتيوب (دالة مزيفة)
async def check_youtube_subscription(update: Update, context: CallbackContext):
    # زر "اشترك" أولاً، ثم زر "تحقق"
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في القناة", url=YOUTUBE_CHANNEL_URL)],
        [InlineKeyboardButton("✅ تحقق", callback_data='check_youtube_subscription')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🚫 **عذرًا، عليك الاشتراك في قناة يوتيوب أولاً**:\n\n📢 القناة: [اضغط هنا للاشتراك](https://youtube.com/@l7aj.1m)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# فك التشفير باستخدام marshal
def decompile_code(encoded_data):
    try:
        decoded_code = marshal.loads(encoded_data)  # فك الشيفرة
        if isinstance(decoded_code, (bytes, bytearray)):
            return None, "البيانات المفكوكة ليست كود Python."
        else:
            disassembly = dis.Bytecode(decoded_code).dis()
            return decoded_code, disassembly
    except Exception as e:
        return None, f"حدث خطأ أثناء فك الشيفرة: {str(e)}"

# معالجة الرسائل لفك التشفير
async def handle_decrypt(update: Update, context: CallbackContext) -> None:
    try:
        encoded_data = eval(update.message.text)  # تحويل النص إلى بيانات مشفرة
        if not isinstance(encoded_data, (bytes, bytearray)):
            await update.message.reply_text("البيانات التي أرسلتها ليست بصيغة مشفرة صحيحة.")
            return

        # فك تشفير الكود
        decoded_code, result_decompiled = decompile_code(encoded_data)
        if decoded_code is None:
            await update.message.reply_text(result_decompiled)  # رسالة خطأ
        else:
            # إعداد نص التعليمات المفككة
            result_message = f"تم فك التشفير:\n{result_decompiled}"

            # إذا كان النص المفكك طويلًا جدًا، سيتم إرساله عبر ملف
            if len(result_decompiled) > 4096:  # الحد الأقصى لعدد الحروف في الرسالة
                # إنشاء ملف يحتوي على التعليمات المفككة
                file_content = f"# التعليمات المفككة:\n\n{result_decompiled}"
                file = BytesIO(file_content.encode('utf-8'))
                file.name = "تم فك تشفيره.txt"

                # إرسال النص والملف
                await update.message.reply_text("\n\n 🗂نظرًا لطول الرسالة، تم إرسالها عبر ملف."
                  "\n\n بعد فك تشفير قم بأخد الكود و دخل الى  CHAT GBT  وكتب له قم بترتيب هذا لكود و تحويله الى كود بايثون 📝🩵")                            
                                                                  
                await update.message.reply_document(InputFile(file, filename="تم_فك_تشفيره.txt"))
            else:
                await update.message.reply_text(result_message)  # إرسال النص المفكك مباشرة
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء معالجة الكود المشفر: {str(e)}")

# وظيفة بدء البوت
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    # إرسال رسالة ترحيب للمستخدم مع توضيح وظيفة البوت
    welcome_message = (
        "👋 مرحبًا! \n\n"
        "أنا بوت فك التشفير. يمكنك إرسال بيانات مشفرة بصيغة marshal، وسأساعدك في فك تشفيرها وعرض التعليمات. "
        "لكن أولًا، عليك الاشتراك في قناة يوتيوب الخاصة بنا لتتمكن من استخدام البوت. "
        "اضغط على الزر أدناه للتحقق من اشتراكك في القناة."
      " \n\n [المطور] (@l7l7aj)"
    )
    
    # إرسال رسالة الترحيب
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

    # تحقق من الاشتراك في قناة يوتيوب
    await check_youtube_subscription(update, context)

# معالجة الأزرار
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "check_youtube_subscription":
        # بمجرد الضغط على "تحقق"، سيتم عرض الأزرار الرئيسية
        keyboard = [
            [InlineKeyboardButton("🔓 تفعيل فك التشفير", callback_data='decrypt')],
        ]
        if query.from_user.id == ADMIN_ID:
            keyboard.append([
                InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"),
                InlineKeyboardButton("📢 الإذاعة", callback_data="broadcast")
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ تم التحقق بنجاح! يمكنك الآن استخدام البوت",
            reply_markup=reply_markup
        )

    elif query.data == "decrypt":
        await query.edit_message_text(
            "من فضلك أرسل الكود المشفر لفك تشفيره.\n\n"
            "ملاحظة📝: يجب أن يكون تنسيق الكود الذي رسله مثل هكذا:\n"
            "b'\\xe3\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\xf3<\\x00\\x00\\x00'\n\n"
            "🩵وشكرا لك"
        )
    elif query.data == "stats":
        await query.edit_message_text(get_stats())
    elif query.data == "broadcast":
        await query.edit_message_text("📢 قسم الإذاعة.")
    else:
        await query.edit_message_text("🚫 هذا الخيار غير متاح.")

# وظيفة الحصول على الإحصائيات
def get_stats():
    try:
        with open("users.txt", 'r') as f:
            users = f.readlines()

        users_count = len(users)
        active_users = len([user for user in users if user.strip().endswith(",active")])  # المستخدمين النشطين
        stats_message = f"\n\n📊 الإحصائيات:\n\n👥 عدد مستخدمي البوت: {users_count}\n🌟 عدد المستخدمين النشطين: {active_users}"
        return stats_message
    except Exception as e:
        return f"حدث خطأ في الحصول على الإحصائيات: {str(e)}"

# إشعار عند انضمام مستخدم جديد
async def welcome(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    # إشعار للمسؤول
    if user.id != ADMIN_ID:
        return  # فقط المسؤول يمكنه تلقي الإشعار

    message = f"🚨 **انضم مستخدم جديد!**\n\n"
    message += f"👤 **الاسم**: {user.first_name} {user.last_name if user.last_name else ''}\n"
    message += f"🔸 **الاسم المستخدم**: @{user.username}\n"
    message += f"🆔 **ID**: {user.id}\n"

    await context.bot.send_message(ADMIN_ID, message)

# تسجيل الأخطاء
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# وظيفة بدء التطبيق
def main():
    # إعداد التطبيق
    application = Application.builder().token(BOT_TOKEN).build()

    # تسجيل المعالجين
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))  # معالج الأزرار
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_decrypt))  # فك التشفير
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))  # إشعار عند انضمام مستخدم جديد

    # تسجيل الأخطاء
    application.add_error_handler(error)

    # بدء التطبيق
    application.run_polling()

if __name__ == '__main__':
    main()
