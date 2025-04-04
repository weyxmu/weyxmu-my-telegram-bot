import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from datetime import datetime

import telebot


TOKEN = "7638159940:AAHvaop2L2ti4MSoxYEYjQ6kj-yGcSG3QTQ"
CHANNEL_ID = "@shodlik_project"
ADMIN_ID = 1649950549  # Sizning Telegram ID’ingiz

logging.basicConfig(
    level=logging.INFO,
    filename='D:/bot/bot.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect("base.db", check_same_thread=False)
cursor = conn.cursor()

# Jadval yaratish (users va purchases)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_name TEXT,
        phone_number TEXT,
        action TEXT,
        timestamp TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_name TEXT,
        course_name TEXT,
        price TEXT,
        timestamp TEXT,
        payment_proof TEXT
    )
''')

# purchases jadvaliga price ustunini qo‘shish (agar mavjud bo‘lmasa)
try:
    cursor.execute("ALTER TABLE purchases ADD COLUMN price TEXT")
except sqlite3.OperationalError:
    pass  # Agar ustun allaqachon mavjud bo‘lsa, hech narsa qilmaymiz

conn.commit()

def log_action(user_id, user_name, phone_number, action):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO users (user_id, user_name, phone_number, action, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (user_id, user_name, phone_number, action, now))
    conn.commit()

def log_purchase(user_id, user_name, course_name, price, payment_proof):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO purchases (user_id, user_name, course_name, price, timestamp, payment_proof) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, user_name, course_name, price, now, payment_proof))
    conn.commit()

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1️⃣ Xizmat turlari"), KeyboardButton(text="2️⃣ Kurslar narxlari")],
        [KeyboardButton(text="3️⃣ Murojat"), KeyboardButton(text="4️⃣ Biz haqimizda")],
        [KeyboardButton(text="5️⃣ Manzil"), KeyboardButton(text="6️⃣ Kurs sotib olish")]
    ],
    resize_keyboard=True
)

back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Ortga")]],
    resize_keyboard=True
)

courses_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Web Dasturlash - 500,000 so‘m", callback_data="course_web")],
    [InlineKeyboardButton(text="Mobil Ilovalar - 400,000 so‘m", callback_data="course_mobile")],
    [InlineKeyboardButton(text="🔙 Ortga", callback_data="back_to_menu")]
])

@dp.message(lambda message: message.text == "/start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Bot ishga tushdi")

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_ID[1:]}")],
        [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subscription")]
    ])
    await message.answer("Botdan foydalanish uchun quyidagi kanalga obuna bo‘ling:", reply_markup=inline_kb)

@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name or "Anonim"
    
    try:
        logging.info(f"Checking subscription for user {user_id} in channel {CHANNEL_ID}")
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        logging.info(f"User status: {member.status}")
        
        if member.status in ["member", "administrator", "creator"]:
            log_action(user_id, user_name, "Noma'lum", "Kanalga obuna bo‘ldi")
            await callback.message.delete()
            await bot.send_message(callback.from_user.id, "Rahmat! Endi telefon raqamingizni yuboring:", reply_markup=phone_keyboard)
        else:
            await callback.answer("Siz hali kanalga obuna bo‘lmagansiz. Iltimos, obuna bo‘ling!", show_alert=True)
    except Exception as e:
        logging.error(f"Error checking subscription: {str(e)}")
        await callback.answer("Xatolik yuz berdi. Qaytadan urinib ko‘ring.", show_alert=True)

@dp.message(lambda message: message.contact is not None)
async def contact_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    phone_number = message.contact.phone_number
    log_action(user_id, user_name, phone_number, "Telefon raqam yuborildi")
    
    await message.answer("Telefon raqamingiz tasdiqlandi! Quyidagi menyudan tanlang:", reply_markup=main_menu)

@dp.message(lambda message: message.text == "1️⃣ Xizmat turlari")
async def services_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Xizmat turlari tanlandi")
    
    text = "Bizning xizmat turlarimiz:\n1. Web dasturlash\n2. Mobil ilovalar"
    await message.answer(text, reply_markup=back_button)

@dp.message(lambda message: message.text == "2️⃣ Kurslar narxlari")
async def prices_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Kurslar narxlari tanlandi")
    
    text = "Kurslar narxlari:\n1. Web dasturlash - 500,000 so‘m\n2. Mobil ilovalar - 400,000 so‘m"
    await message.answer(text, reply_markup=back_button)

@dp.message(lambda message: message.text == "3️⃣ Murojat")
async def contact_us_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Murojat tanlandi")
    
    text = "Biz bilan bog‘lanish: @ShodlikShavkatov"
    await message.answer(text, reply_markup=back_button)

@dp.message(lambda message: message.text == "4️⃣ Biz haqimizda")
async def about_us_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Biz haqimizda tanlandi")
    
    text = "Biz IT sohasida tajribali jamoamiz. Maqsadimiz - sifatli ta’lim va xizmatlar taqdim etish."
    await message.answer(text, reply_markup=back_button)

@dp.message(lambda message: message.text == "5️⃣ Manzil")
async def location_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Manzil tanlandi")
    
    text = "Manzilimiz: Xonqa Tumani, Tong-yulduzi ko‘chasi 47-uy"
    await message.answer(text, reply_markup=back_button)

@dp.message(lambda message: message.text == "🔙 Ortga")
async def back_to_menu(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Ortga qaytdi")
    await message.answer("Asosiy menyu:", reply_markup=main_menu)

# Kurs sotib olish menyusi
@dp.message(lambda message: message.text == "6️⃣ Kurs sotib olish")
async def buy_course_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    log_action(user_id, user_name, "Noma'lum", "Kurs sotib olish tanlandi")
    
    await message.answer("Quyidagi kurslardan birini tanlang:", reply_markup=courses_menu)

# Kurs haqida ma’lumot
@dp.callback_query(lambda c: c.data in ["course_web", "course_mobile"])
async def show_course_info(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name or "Anonim"
    course_name = "Web Dasturlash" if callback.data == "course_web" else "Mobil Ilovalar"
    price = "500,000 so‘m" if callback.data == "course_web" else "400,000 so‘m"
    
    course_info = f"📚 Kurs: {course_name}\n" \
                  f"💰 Narxi: {price}\n" \
                  f"ℹ️ Ma’lumot: Ushbu kursda siz {course_name.lower()} bo‘yicha zamonaviy bilimlarni o‘rganasiz."
    
    buy_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Sotib olish", callback_data=f"buy_{course_name.lower().replace(' ', '_')}")],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="back_to_courses")]
    ])
    
    await callback.message.edit_text(course_info, reply_markup=buy_button)
    log_action(user_id, user_name, "Noma'lum", f"{course_name} haqida ma’lumot ko‘rildi")

# Kurs sotib olish jarayoni
@dp.callback_query(lambda c: c.data in ["buy_web_dasturlash", "buy_mobil_ilovalar"])
async def process_course_purchase(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name or "Anonim"
    course_name = "Web Dasturlash" if callback.data == "buy_web_dasturlash" else "Mobil Ilovalar"
    price = "500,000 so‘m" if callback.data == "buy_web_dasturlash" else "400,000 so‘m"
    
    await callback.message.delete()
    await bot.send_message(user_id, f"Siz {course_name} kursini sotib olmoqchisiz. Narxi: {price}.\n"
                                    "To‘lovni quyidagi karta raqamiga amalga oshiring:\n"
                                    "Karta: 5614 6818 1268 7691\n"
                                    "To‘lov qilgandan so‘ng, chekni skrinshot qilib shu yerga yuboring.")
    log_action(user_id, user_name, "Noma'lum", f"{course_name} kursini sotib olishni boshladi")

# To‘lov chekini qabul qilish
@dp.message(lambda message: message.photo)
async def handle_payment_proof(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Anonim"
    
    cursor.execute("SELECT action FROM users WHERE user_id = ? AND action LIKE '%kursini sotib olishni boshladi' ORDER BY timestamp DESC LIMIT 1", (user_id,))
    last_action = cursor.fetchone()
    
    if last_action:
        course_name = last_action[0].replace(" kursini sotib olishni boshladi", "")
        price = "500,000 so‘m" if course_name == "Web Dasturlash" else "400,000 so‘m"
        log_purchase(user_id, user_name, course_name, price, "Photo")
        
        # Foydalanuvchiga xabar
        await message.answer("Sizning murojaatingiz qabul qilindi. Admin siz bilan 10 daqiqa ichida bog‘lanadi.")
        
        # Adminga xabar va rasm yuborish
        photo_id = message.photo[-1].file_id  # Eng katta o‘lchamdagi rasmni olish
        await bot.send_message(ADMIN_ID, f"Foydalanuvchi: {user_name} (ID: {user_id})\n"
                                        f"Kurs: {course_name}\n"
                                        f"Narxi: {price}\n"
                                        f"To‘lov cheki qabul qilindi: Photo")
        await bot.send_photo(ADMIN_ID, photo_id)
    else:
        await message.answer("Avval kursni tanlang va to‘lovni amalga oshiring!")

# Admin statistikasi
@dp.message(lambda message: message.text == "/stats")
async def stats_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users")
        action_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM purchases")
        purchase_count = cursor.fetchone()[0]
        
        text = f"📊 Bot statistikasi:\n" \
               f"Foydalanuvchilar soni: {user_count}\n" \
               f"Umumiy harakatlar soni: {action_count}\n" \
               f"Sotib olingan kurslar soni: {purchase_count}"
        await message.answer(text)
    else:
        await message.answer("Bu buyruq faqat admin uchun mavjud!")

# Ortga qaytish (kurs menyusidan)
@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, "Asosiy menyu:", reply_markup=main_menu)

@dp.callback_query(lambda c: c.data == "back_to_courses")
async def back_to_courses(callback: types.CallbackQuery):
    await callback.message.edit_text("Quyidagi kurslardan birini tanlang:", reply_markup=courses_menu)

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())


TOKEN = "7638159940:AAHvaop2L2ti4MSoxYEYjQ6kj-yGcSG3QTQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Assalomu alaykum!")

print("Bot ishga tushdi...")
bot.polling(none_stop=True)
