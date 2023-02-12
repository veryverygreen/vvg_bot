import speech_recognition as sr
from aiogram import types
import datetime, random, psycopg2
from config import db_name, db_user, db_password, db_host

def tuple_to_int(a:tuple):
    a = str(a)
    a = a[:0] + a[1:]
    a = a[:-1]
    a = a[:-1]
    a = int(a)
    return a

def tuple_to_str (a:tuple):
    a = str(a)
    a = a[:0] + a[1:]
    a = a[:0] + a[1:]
    a = a[:-1]
    a = a[:-1]
    a = a[:-1]
    return a

def audio_to_text(dest_name: str):
# Функция для перевода аудио в текст
    r = sr.Recognizer() 
    # тут мы читаем наш .vaw файл
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU") # используя возможности библиотеки распознаем текст, так же тут можно изменять язык распознавания
    return result

def username (message: types.Message): #нужна для корректного отображения пользователя, т.к. в telegram может не быть username или фамилии
    username = str(message.from_user.username)
    if username != None:
        user_id=username
    else:
        name = str(message.from_user.id)
        first_name = str(message.from_user.first_name)
        last_name = str(message.from_user.last_name)
        if name.isdigit() == True:
            if last_name == None:
                user_id = first_name
            else:
                user_id = first_name + last_name
        else:
            user_id = name
    return user_id

def reg(message: types.Message):
    conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
    conn.autocommit = True
    cursor = conn.cursor()
    chat_id = message.chat.id
    user_id=username(message)
    cursor.execute(f"SELECT MAX(smb_id) FROM smb")
    counter = tuple_to_int(cursor.fetchone())
    counter +=1
    mas = (counter, user_id, chat_id, 0)
    cursor.execute(f"SELECT COUNT(*) FROM smb WHERE chat_id={chat_id} AND user_id='{user_id}'")
    check = tuple_to_int(cursor.fetchone())

    if check == 1:
        reg_text = "Ты уже в игре"
    else:
        cursor.execute(f"INSERT INTO smb (smb_id, user_id, chat_id, score) VALUES {mas} ")
        reg_text = "Теперь ты в игре"
    cursor.close()
    conn.close()
    return reg_text

def first_choice(chat_id): #выбор победителя, если игра проводится впервые
    conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"SELECT smb_id FROM smb WHERE chat_id={chat_id}")
    winner = tuple_to_int(random.choice(cursor.fetchall()))  # id победителя
    cursor.execute(f"SELECT score FROM smb WHERE chat_id={chat_id} AND smb_id={winner}")
    score = tuple_to_int(random.choice(cursor.fetchall()))  # счет победителя
    score += 1
    days = str(datetime.date.today())
    cursor.execute(f"INSERT INTO smb_time(days, chat_id) VALUES('{days}', {chat_id})")
    cursor.execute(f"UPDATE smb SET score={score} WHERE smb_id={winner} AND chat_id={chat_id}")
    cursor.execute(f"SELECT user_id FROM smb WHERE smb_id={winner} AND chat_id={chat_id}")
    result = tuple_to_str(cursor.fetchone())
    cursor.execute(f"UPDATE smb_time SET user_id = '{result}' WHERE chat_id={chat_id}")
    output_message = (f"А кто-то дня сегодня @{result}")
    cursor.close()
    conn.close()
    return output_message

def second_choice(chat_id):
    conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
    conn.autocommit = True
    cursor = conn.cursor()
    days = str(datetime.date.today())
    cursor.execute(f"SELECT days FROM smb_time WHERE chat_id={chat_id}")  # дата последнего выбора
    last_day = tuple_to_str(cursor.fetchone())
    if days == last_day:
        cursor.execute(f"SELECT user_id FROM smb_time WHERE chat_id={chat_id}")
        result = tuple_to_str(cursor.fetchone()) # последний победитель
        output_message = (f"Сегодня кто-то дня уже выбран - @{result}")
    else:
        cursor.execute(f"SELECT smb_id FROM smb WHERE chat_id={chat_id}")
        winner = tuple_to_int(random.choice(cursor.fetchall()))  # id победителя
        cursor.execute(f"SELECT score FROM smb WHERE chat_id={chat_id} AND smb_id={winner}")
        score = tuple_to_int(random.choice(cursor.fetchall()))  # счет победителя
        score += 1
        cursor.execute(f"UPDATE smb_time SET days='{days}' WHERE chat_id={chat_id}")
        cursor.execute(f"UPDATE smb SET score={score} WHERE smb_id={winner} AND chat_id={chat_id}")

        cursor.execute(f"SELECT user_id FROM smb WHERE smb_id={winner} AND chat_id={chat_id}")
        result = tuple_to_str(cursor.fetchone())
        cursor.execute(f"UPDATE smb_time SET user_id='{result}' WHERE chat_id={chat_id}")
        output_message = (f"А кто-то дня сегодня @{result}")
        cursor.close()
        conn.close()
    return output_message

def smb(message: types.Message):
    global output_message
    conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
    conn.autocommit = True
    cursor = conn.cursor()
    chat_id = int(message.chat.id)
    cursor.execute(f"SELECT COUNT(*) FROM smb WHERE chat_id={chat_id}")
    player = tuple_to_int(cursor.fetchone())  # наличие участников в игре
    if player == 0:
        output_message = "В игре пока нет участников"
    else:
        cursor.execute(f"SELECT COUNT(*) FROM smb_time WHERE chat_id={chat_id}")
        check_choice = tuple_to_int(cursor.fetchone())
        cursor.close()
        conn.close()
        if check_choice == 1:
            output_message = second_choice(chat_id)
        else:
            output_message = first_choice(chat_id)
    return output_message

def stats(message):
    chat_id=str(message.chat.id)
    conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"SELECT count(*) FROM smb WHERE chat_id='{chat_id}'")
    total = int(cursor.fetchone()[0])
    cursor.execute(f"SELECT user_id FROM smb WHERE chat_id='{chat_id}' ORDER BY score DESC")
    query_results = list(cursor.fetchall())
    cursor.execute(f"SELECT score FROM smb WHERE chat_id='{chat_id}' ORDER BY score DESC")
    query_results1 = list(cursor.fetchall())
    i = 0
    query_text = ("")
    while i < total:
        query_results_index = tuple_to_str(query_results[i])
        query_results_index1 = tuple_to_int(query_results1[i])
        query_text += (f"{i + 1}. {query_results_index} - {query_results_index1} раз(а)\n")
        i += 1
    cursor.close()
    conn.close()
    return [query_text,total]
