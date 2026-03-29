import telebot
import google.generativeai as genai

# --- الإعدادات الخاصة بك (جاهزة 100%) ---
BOT_TOKEN = "8596552294:AAE8RX2puvGGkUtC0nX4rnpxnAssLZEgEt0"
GEMINI_KEY = "AIzaSyDP9Rf-0k2FjcSrwki4TjRocbVyznGmSRQ"

# تهيئة البوت وجميناي
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ذاكرة المستخدمين (لحفظ الشعبة والسؤال الحالي)
user_data = {}

# قائمة الشعب الجزائرية
MAJORS = ['علوم تجريبية', 'رياضيات', 'تقني رياضي', 'آداب وفلسفة', 'لغات أجنبية', 'تسيير واقتصاد']

# --- أوامر البوت ---

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for major in MAJORS:
        markup.add(major)
    
    bot.send_message(message.chat.id, 
                     "أهلاً بيك في 'الباك في الجيب'! 🎓\n"
                     "أنا رفيقك الدراسي الذكي. اختر شعبتك لنبدأ المراجعة:", 
                     reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in MAJORS)
def set_major(message):
    user_data[message.from_user.id] = {"major": message.text, "q": None}
    bot.send_message(message.chat.id, 
                     f"تم تسجيلك كطالب {message.text}. ✅\n"
                     "راني واجد! أرسل /ask باش نبعتلك سؤال من الباك.")

@bot.message_handler(commands=['ask'])
def send_question(message):
    uid = message.from_user.id
    if uid not in user_data:
        bot.reply_to(message, "اختر شعبتك أولاً بـ /start يا البطل!")
        return

    major = user_data[uid]['major']
    
    # طلب سؤال من جيمناي بلهجة جزائرية
    prompt = f"أنت 'رفيق الباك'، طالب جزائري مرح. ولد سؤالاً واحداً حقيقياً من بكالوريا الجزائر لشعبة {major}. صغه بالدارجة الجزائرية كأنك تطلب مساعدة. لا تعطي الحل."
    
    try:
        response = model.generate_content(prompt)
        user_data[uid]['q'] = response.text
        bot.send_message(message.chat.id, response.text)
    except:
        bot.send_message(message.chat.id, "كاين ضغط على السيرفر، عاود جرب /ask!")

@bot.message_handler(func=lambda m: True)
def evaluate_answer(message):
    uid = message.from_user.id
    if uid not in user_data or not user_data[uid].get('q'):
        return

    question = user_data[uid]['q']
    major = user_data[uid]['major']
    
    eval_prompt = f"أنت 'رفيق الباك'. سألت سؤالاً: {question}. الطالب (شعبة {major}) أجاب: {message.text}. قيم إجابته بالدارجة الجزائرية، شجعه إذا صح وصحح له إذا أخطأ."
    
    try:
        response = model.generate_content(eval_prompt)
        bot.reply_to(message, response.text)
        user_data[uid]['q'] = None # تصفير السؤال
    except:
        bot.reply_to(message, "حدث خطأ بسيط، حاول مرة أخرى!")

# تشغيل البوت بشكل مستمر
if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling()
            
