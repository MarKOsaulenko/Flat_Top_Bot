import telebot
from telebot import types
import psycopg2
from config import host,user,password,db_name,TOKEN



bot = telebot.TeleBot(TOKEN)


#Глобальные переменные
fr_name = None
fr_adress = None
fr_ph_number = None
name = None
ph_number = None
flat  = None
adress = None
budget = None
area = None
dop_info = None
application = None
fr_application = None


@bot.message_handler(commands=['start'])
def gritting(message):
    global user_id  # Для системы рефералов
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (id serial PRIMARY KEY,
                 name varchar(50),
                 phone_number varchar(50) NOT NULL,
                 application text)''')
        connection.close()
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b_reg = types.KeyboardButton('Зарегистрироваться')
    b_autorize = types.KeyboardButton('Авторизироваться')
    markup.row(b_reg,b_autorize)
    bot.send_message(message.chat.id,'Добро пожаловать! Я помогу вам найти квартиру или коммерческое помещение. Также вы можете порекомендовать своим друзьям и получить бонусы. Для начала зарегистрируйтесть или авторизируйтесь',reply_markup=markup)
    bot.register_next_step_handler(message,choice)

def choice(message):
    text = message.text.strip()
    del_markup = types.ReplyKeyboardRemove()
    if text == 'Зарегистрироваться':
        bot.send_message(message.chat.id,'Укажите номер телефона',reply_markup=del_markup)
        bot.register_next_step_handler(message,registration)
    elif text == 'Авторизироваться':
        bot.send_message(message.chat.id, 'Укажите номер телефона',reply_markup=del_markup)
        bot.register_next_step_handler(message, autorization)
    #else:
        #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #b_reg = types.KeyboardButton('Зарегистрироваться')
        #b_autorize = types.KeyboardButton('Авторизироваться')
        #markup.row(b_reg, b_autorize)
        #bot.send_message(message.chat.id,'Повторите попытку',reply_markup=markup)

def autorization(message):
    global ph_number,name
    ph_number = message.text.strip()
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute('''SELECT name, phone_number
                          FROM users
                          WHERE phone_number = ('%s')'''% (ph_number))
        data = cursor.fetchall()
        data2 = []
        for el in data:
            data2.append(el[0])
            data2.append(el[1])
        if ph_number in data2:
            name = data2[0]
            markup = types.InlineKeyboardMarkup()
            b_application = types.InlineKeyboardButton('Оставить заявку', callback_data='app')
            b_recommendation = types.InlineKeyboardButton('Рекомендовать друга', callback_data='rec')
            b_my_app = types.InlineKeyboardButton('Мои заявки', callback_data='my_app')
            b_faq = types.InlineKeyboardButton('Тех. поддержка', callback_data='faq')
            markup.add(b_application, b_recommendation, b_my_app, b_faq, row_width=2)
            bot.send_message(message.chat.id,f'Приветствую Вас, {name}',reply_markup=markup)
            connection.close()
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('Зарегистрироваться'))
            bot.send_message(message.chat.id, 'Такого пользователя нет, зарегестрируйтесь',reply_markup=markup)
            bot.register_next_step_handler(message, choice)

def registration(message):
    global ph_number
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,registration)
        return
    ph_number = message.text.strip()
    bot.send_message(message.chat.id,'Напишите Ваше имя')
    bot.register_next_step_handler(message,registration_step)

def registration_step(message):
    global name
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,registration_step)
        return
    name = message.text.strip()
    markup = types.InlineKeyboardMarkup()
    b_application = types.InlineKeyboardButton('Оставить заявку', callback_data='app')
    b_recommendation = types.InlineKeyboardButton('Рекомендовать друга', callback_data='rec')
    b_my_app = types.InlineKeyboardButton('Мои заявки', callback_data='my_app')
    b_faq = types.InlineKeyboardButton('Тех. поддержка', callback_data='faq')
    markup.add(b_application,b_recommendation,b_my_app,b_faq,row_width=2)
    bot.send_message(message.chat.id,f'''Приятно с Вами познакомиться, {name}! Регистрация прошла успешно!
                                            \nТеперь выберите действие из списка''',reply_markup=markup)


@bot.callback_query_handler(func = lambda callback: True)
def callbacking(callback):
    global flat
    if callback.data == 'app':
        markup = types.InlineKeyboardMarkup()
        b_flat = types.InlineKeyboardButton('Квартира', callback_data = 'flat')
        b_comerical = types.InlineKeyboardButton('Коммерческое помещение', callback_data = 'commers')
        markup.add(b_flat,b_comerical,row_width=1)
        bot.edit_message_text('Отлично! Давайте создадим заявку. Пожалуйста, выберите тип недвижимости',callback.message.chat.id,callback.message.message_id,reply_markup=markup)
    elif callback.data == 'rec':
        markup = types.InlineKeyboardMarkup()
        b_flat = types.InlineKeyboardButton('Квартира', callback_data='friend_flat')
        b_comerical = types.InlineKeyboardButton('Коммерческое помещение', callback_data='friend_commers')
        markup.add(b_flat, b_comerical, row_width=1)
        bot.edit_message_text('Отлично! Какой тип недвижимости он рассматривает?',callback.message.chat.id, callback.message.message_id,reply_markup=markup)
    elif callback.data == 'my_app':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Вернуться в главное меню', callback_data='go_back'))
        markup2 = types.InlineKeyboardMarkup()
        markup2.add(types.InlineKeyboardButton('Cоздать', callback_data='app'))
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('''SELECT application
                            FROM users
                            WHERE phone_number = ('%s')''' % (ph_number))
            my_app = cursor.fetchall()
            data = ''
            for i in my_app:
                data =  data + i[0] + '\n'
            connection.close()
        if data != '':
            bot.send_message(callback.message.chat.id,f'Все ваши заявки:\n{data}',reply_markup=markup)
        else:
            bot.send_message(callback.message.chat.id, f'У вас пока нет заявок, но вы можете её создать!', reply_markup=markup2)
    elif callback.data == 'go_back':
        markup = types.InlineKeyboardMarkup()
        b_application = types.InlineKeyboardButton('Оставить заявку', callback_data='app')
        b_recommendation = types.InlineKeyboardButton('Рекомендовать друга', callback_data='rec')
        b_my_app = types.InlineKeyboardButton('Мои заявки', callback_data='my_app')
        b_faq = types.InlineKeyboardButton('Тех. поддержка', callback_data='faq')
        markup.add(b_application, b_recommendation, b_my_app, b_faq, row_width=2)
        bot.edit_message_text('Выберите действие из списка',callback.message.chat.id,callback.message.message_id,reply_markup=markup)
    elif callback.data == 'friend_flat':
        flat = 'Квартира'
        bot.send_message(callback.message.chat.id,'Напишите местоположение, о котором заинтересован друг.\nПример: область, район, населённый пункт')
        bot.register_next_step_handler(callback.message,friend_reg)
    elif callback.data == 'friend_commers':
        flat = 'Коммерческое помещение'
        bot.send_message(callback.message.chat.id,'Напишите местоположение, о котором заинтересован друг.\nПример: область, район, населённый пункт')
        bot.register_next_step_handler(callback.message, friend_reg)
    elif callback.data == 'faq':
        markup = types.InlineKeyboardMarkup()
        b_link = types.InlineKeyboardButton('Клик',url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        markup.add(b_link)
        bot.send_message(callback.message.chat.id,'Перейдите по ссылке',reply_markup=markup)
    elif callback.data == 'commers':
        flat = 'Коммерческое помещение'
        bot.send_message(callback.message.chat.id,'Напишите местоположение, которое вас интересует.\nПример: область, район, населённый пункт',parse_mode='html')
        bot.register_next_step_handler(callback.message,adress_def)
    elif callback.data == 'flat':
        flat = 'Квартира'
        bot.send_message(callback.message.chat.id,'Напишите местоположение, которое вас интересует.\nПример: область, район, населённый пункт',parse_mode='html')
        bot.register_next_step_handler(callback.message,adress_def)
    elif callback.data == 'succsessfully':
        connection = psycopg2.connect(
            user = user,
            password = password,
            database = db_name,
            host = host
        )
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(f'''INSERT INTO users (name, phone_number, application)
                        VALUES ('%s', '%s', '%s')''' % (name, ph_number, application)
            )
            connection.close()
        markup = types.InlineKeyboardMarkup()
        b_back_to_main_menu = types.InlineKeyboardButton('Вернуться в главное меню',callback_data = 'go_back')
        b_create_new = types.InlineKeyboardButton('Создать новую заявку',callback_data = 'app')
        b_recommendation = types.InlineKeyboardButton('Рекомендовать друга', callback_data='rec')
        b_my_app = types.InlineKeyboardButton('Мои заявки', callback_data='my_app')
        b_faq = types.InlineKeyboardButton('Тех. поддержка', callback_data='faq')
        markup.add(b_back_to_main_menu)
        markup.add(b_create_new,b_recommendation,b_my_app,b_faq,row_width=2)
        bot.edit_message_text('Заявка передана в работу! В ближайшее время позвонит менеджер.\nКакие следующие действия?',callback.message.chat.id,callback.message.message_id,reply_markup=markup)
    elif callback.data == 'succsessfully_fr':
        connection = psycopg2.connect(
            user=user,
            password=password,
            database=db_name,
            host=host
        )
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(f'''INSERT INTO users (name, phone_number, application)
                                VALUES ('%s', '%s', '%s')''' % (name, ph_number, fr_application)
                           )
            connection.close()
        markup = types.InlineKeyboardMarkup()
        b_back_to_main_menu = types.InlineKeyboardButton('Вернуться в главное меню', callback_data='go_back')
        b_create_new = types.InlineKeyboardButton('Создать новую заявку', callback_data='app')
        b_recommendation = types.InlineKeyboardButton('Рекомендовать друга', callback_data='rec')
        b_my_app = types.InlineKeyboardButton('Мои заявки', callback_data='my_app')
        b_faq = types.InlineKeyboardButton('Тех. поддержка', callback_data='faq')
        markup.add(b_back_to_main_menu)
        markup.add(b_create_new, b_recommendation, b_my_app, b_faq, row_width=2)
        bot.edit_message_text(
            'Заявка передана в работу! В ближайшее время позвонит менеджер.\nКакие следующие действия?',
            callback.message.chat.id, callback.message.message_id, reply_markup=markup)
    elif callback.data == 'cancel':
        markup = types.InlineKeyboardMarkup()
        b_go_back_to_menu = types.InlineKeyboardButton('Вернуться в главное меню', callback_data='go_back')
        markup.add(b_go_back_to_menu)
        bot.edit_message_text('Заявка отменена',callback.message.chat.id,callback.message.message_id,reply_markup=markup)

def adress_def(message):
    global adress
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,adress_def)
        return
    adress = message.text
    bot.send_message(message.chat.id, 'Укажите ваш бюджет',parse_mode='html')
    bot.register_next_step_handler(message,budget_def)

def budget_def(message):
    global budget
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,budget_def)
        return
    budget = message.text.strip()
    bot.send_message(message.chat.id,'Какую площадь вы ищете?')
    bot.register_next_step_handler(message,acceptance)
def acceptance(message):
    global area, application
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,acceptance)
        return
    area = message.text
    markup = types.InlineKeyboardMarkup()
    b_acc = types.InlineKeyboardButton('Подтвердить✅', callback_data = 'succsessfully')
    b_cancel = types.InlineKeyboardButton('Отменить❌', callback_data = 'cancel')
    markup.add(b_acc,b_cancel)
    application = f'Тип недвижимости: {flat}, Местоположение: {adress}, Площадь в м²: {area}, Бюджет: {budget}'
    bot.send_message(message.chat.id,f'Тип недвижимости: {flat}\nМестоположение: {adress}\nПлощадь в м²: {area}\nБюджет: {budget}\nКонтактная информация: {name} {ph_number}',reply_markup=markup)

def friend_reg(message):
    global fr_adress
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,friend_reg)
        return
    fr_adress = message.text
    bot.send_message(message.chat.id,'Теперь назовите имя вашего друга')
    bot.register_next_step_handler(message,friend_name)

def friend_name(message):
    global fr_name
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,friend_name)
        return
    fr_name = message.text.strip()
    bot.send_message(message.chat.id, 'И укажите его номер телефона')
    bot.register_next_step_handler(message, friend_ph_number)

def friend_ph_number(message):
    global fr_ph_number
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,friend_ph_number)
        return
    fr_ph_number = message.text.strip()
    bot.send_message(message.chat.id, "Также можете оставить дополнительный комментарий или поставить '-' ")
    bot.register_next_step_handler(message,friend_acc)

def friend_acc(message):
    global dop_info,fr_application
    if '/' in message.text:
        bot.reply_to(message,"'/' нельзя использовать. Повторите попытку" )
        bot.register_next_step_handler(message,friend_acc)
        return
    dop_info = message.text
    markup = types.InlineKeyboardMarkup()
    b_acc = types.InlineKeyboardButton('Подтвердить✅', callback_data='succsessfully_fr')
    b_cancel = types.InlineKeyboardButton('Отменить❌', callback_data='cancel')
    markup.add(b_acc, b_cancel)
    fr_application = f'Тип недвижимости: {flat},Местоположение: {fr_adress},Контактная информация: {fr_name} {fr_ph_number},Доп. информация: {dop_info}'
    bot.send_message(message.chat.id, f'Заявка:\nТип недвижимости: {flat}\nМестоположение: {fr_adress}\nКонтактная информация: {fr_name} {fr_ph_number}\nДоп. информация: {dop_info}', reply_markup=markup)


bot.infinity_polling()
