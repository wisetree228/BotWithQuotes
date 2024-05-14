import telebot
from sqlite3 import connect
from telebot import types
import random
import base64


# Указываем токен бота
TOKEN = 'your_token'

# Создаем объект бота
bot = telebot.TeleBot(TOKEN)



ADMIN_ID="your_admin_id"

d={}
d['l']=[]



# вспомогательные функции для работы с базой данных в коде
def selectAllWithCondition(table, cond):
    db = connect('base.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE {cond};")
    db.commit()
    list = cur.fetchall()
    cur.close()
    db.close()
    return list


def selectOne(table, cond):
    db = connect('base.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE {cond};")
    db.commit()
    list = cur.fetchone()
    cur.close()
    db.close()
    return list

def selectAll(table):
    db = connect('base.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {table};")
    db.commit()
    list = cur.fetchall()
    cur.close()
    db.close()
    return list

def drop(table, cond):
    # Устанавливаем соединение с базой данных
    conn = connect('base.db')
    cur = conn.cursor()
    try:
        # Проверяем наличие активной транзакции перед откатом
        if conn.in_transaction:
            # Если есть активная транзакция, то откатываем ее
            cur.execute("ROLLBACK")

        # Подготавливаем SQL-запрос для удаления
        query = f"DELETE FROM {table} WHERE {cond};"

        # Выполняем запрос
        cur.execute(query)

        # Фиксируем изменения в базе данных
        conn.commit()
        print("Запись успешно удалена.")
    except Exception as e:
        # Откатываем транзакцию в случае ошибки, если она активна
        if conn.in_transaction:
            conn.rollback()
        print(f"Произошла ошибка при удалении записи: {e}")
    finally:
        # Закрываем курсор
        cur.close()
        # Закрываем соединение с базой данных
        conn.close()



def check_id(table, cond):
    db = connect('base.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE {cond};")
    db.commit()
    list = cur.fetchall()
    cur.close()
    db.close()
    if len(list)>=1:
        return True
    return False

def selectOneAll(table):
    db = connect('base.db')
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {table};")
    db.commit()
    list = cur.fetchone()
    cur.close()
    db.close()
    return list



# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    if not(message.chat.id in d['l']):
        d['l'].append(message.chat.id)

    #bot.send_message(message.chat.id, "hi")
    print(message.chat.id, message.from_user.username, message.text)
    if message.chat.id!=ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=2)  # Указываем количество кнопок в ряду
        item1 = types.KeyboardButton("Добавить цитату")
        item2 = types.KeyboardButton("Читать рандомную цитату")
        markup.add(item1, item2)
        bot.send_message(message.chat.id, f"Это бот, который шарит за цитаты Джейсона Стетхема! Предложи свою цитату(отправь админу на модерацию) или читай рандомную цитату! \nАвтор бота и админ: @pppggg228", reply_markup=markup)
    else:
        leng=len(selectAll('predl'))
        markup = types.ReplyKeyboardMarkup(row_width=1)  # Указываем количество кнопок в ряду
        item1 = types.KeyboardButton(f"Смотреть предложку")

        markup.add(item1)
        bot.send_message(ADMIN_ID, f"Посмотреть предложку? ({leng} цитат)", reply_markup=markup)

@bot.message_handler()
def commands_handler(message):
    if not(message.chat.id in d['l']):
        d['l'].append(message.chat.id)

    print(message.chat.id, message.from_user.username, message.text)
    if message.text=="Добавить цитату":
        bot.send_message(message.chat.id, "Введите цитату, которую вы хотите отправить админу:")
        bot.register_next_step_handler(message, forward_to_admin)

    elif message.text=="Смотреть предложку" and message.chat.id==ADMIN_ID:
        quote=selectOneAll('predl')
        if len(selectAll('predl'))!=0:

            markup = types.ReplyKeyboardMarkup(row_width=2)  # Указываем количество кнопок в ряду
            item1 = types.KeyboardButton("Одобрить")
            item2 = types.KeyboardButton("Не одобрить")
            markup.add(item1, item2)
            if quote[4]:
                image_data = base64.b64decode(quote[4])
                bot.send_photo(ADMIN_ID, image_data, caption=f"Цитата от @{quote[2]}:\n{quote[1]}", reply_markup=markup)
            else:
                bot.send_message(ADMIN_ID, f"Цитата от @{quote[2]}:\n{quote[1]}", reply_markup=markup)
        else:
            bot.send_message(ADMIN_ID, 'цитат нет, предложка пустая')

    elif message.text=="Одобрить" and message.chat.id==ADMIN_ID:
        quote = selectOneAll('predl')


        con = connect('base.db')
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO quotes (text, author, chat, img) VALUES (?, ?, ?, ?)", (quote[1], quote[2], quote[3], quote[4]))
            cur.execute(f'DELETE FROM predl WHERE id={quote[0]};')
            con.commit()
            id = quote[3]
            bot.send_message(id, f"Ваша цитата \n{quote[1]} \nодобрена!")
        except Exception as e:
            print(f"Ошибка при обработке цитаты: {e}")
            con.rollback()
        finally:
            cur.close()
            con.close()

    elif message.text=="Не одобрить" and message.chat.id==ADMIN_ID:
        quote = selectOneAll('predl')

        #drop('predl', f"id={quote[0]};")

        con = connect('base.db')
        cur = con.cursor()
        try:
            cur.execute(f'DELETE FROM predl WHERE id={quote[0]};')
            con.commit()
            id = quote[3]
            bot.send_message(id, f"Ваша цитата \n{quote[1]} \nне одобрена!")
        except Exception as e:
            print(f"Ошибка при обработке цитаты: {e}")
            con.rollback()
        finally:
            cur.close()
            con.close()

    elif message.text=="Читать рандомную цитату":
        ID=message.chat.id
        if len(selectAll('quotes'))!=0:

            con = connect('base.db')
            cur = con.cursor()
            list= {}
            list['u']=""
            list['t']=""
            list['i']=""
            try:
                cur.execute("SELECT * FROM quotes;")
                con.commit()
                ll=cur.fetchall()
                l=random.choice(ll)
                list['u']=l[2]
                list['t']=l[1]
                list['i']=l[4]


            except Exception as e:
                print(f"Ошибка при обработке цитаты: {e}")
                con.rollback()
            finally:
                cur.close()
                con.close()
            if list['i']:
                image_data = base64.b64decode(list['i'])
                bot.send_photo(ID, image_data, caption=f"Цитата от @{list['u']}:\n{list['t']}")
            else:
                bot.send_message(ID, f"Цитата от @{list['u']} \n{list['t']}")
        else:
            bot.send_message(message.chat.id, f"Цитат пока нет! Но ты можешь добавить и отправить админу на модерацию")
    elif message.text=="Del" and message.chat.id==ADMIN_ID:
        bot.send_message(ADMIN_ID, "Напиши цитату которую сейчас удалишь")
        bot.register_next_step_handler(message, delmes)









def delmes(message):
    print(message.chat.id, message.from_user.username, message.text)
    con = connect('base.db')
    cur = con.cursor()
    try:
        q=selectOne('quotes', f"text='{message.text}'")
        cur.execute(f"DELETE FROM quotes WHERE text='{message.text}';")
        con.commit()
        bot.send_message(q[3], f"Ваша цитата \n{message.text} \nудалена админом @pppggg228")

    except Exception as e:
        print(f"Ошибка при удалении цитаты: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при удалении: {e}")
        con.rollback()
    finally:
        cur.close()
        con.close()





def forward_to_admin(message):
    print(message.chat.id, message.from_user.username, message.text)

    if message.content_type=='photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_data = base64.b64encode(downloaded_file)
    else:
        image_data=None



    bot.send_message(ADMIN_ID, f"Новая цитата от пользователя @{message.from_user.username}")
    bot.send_message(message.chat.id, "Ваша цитата успешно отправлена админу.")
    con=connect('base.db')
    cur=con.cursor()
    cur.execute(f"INSERT INTO predl (text, author, chat, img) VALUES (?, ?, ?, ?)", (message.caption, message.from_user.username, message.chat.id, image_data))
    con.commit()
    cur.close()
    con.close()


list=selectAll('quotes')

for i in list:
    if not(i[3] in d['l']):
        d['l'].append(i[3])
# for i in d['l']:
#    bot.send_message(i, "Важное обьявление! Бот на время закрывается с целью провердения технических работ, я хочу реализовать возможность добавлять картинки к сообщениям, чтобы превратить бота в сборник мемов. Не пишите боту, пока я не разошлю всем уведомления что всё готово\nОт админа @pppggg228")


#con = connect('base.db')
#cur = con.cursor()
#try:
#
#    cur.execute(f"UPDATE quotes SET text='Лучше иметь сто рублей, чем одного друга-еврея' WHERE text='Лучше иметь сто рублей, чем одного друга-еврея (Артём, не обижайся)'")
#    con.commit()


#except Exception as e:
#    print(f"Ошибка при удалении цитаты: {e}")
#    bot.send_message(ADMIN_ID, f"Ошибка при удалении: {e}")
#    con.rollback()
#finally:
#    cur.close()
#    con.close()

bot.send_message(ADMIN_ID, "Опять перезапуск!\nОт админа @pppggg228")



bot.polling()