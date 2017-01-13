import pymysql
import threading
import requests
import json
import datetime
import re
import time
from retrying import retry
from config import MYSQL_CONN

class MYSQL():
    def __init__(self):
        self.connection = pymysql.connect(**MYSQL_CONN)
        self.cursor = self.connection.cursor()

    def create_table_users(self):
        self.table = 'CREATE TABLE users (chat_id INTEGER, EMAIL TEXT)'
        self.cursor.execute(self.table)

    def insert_lesson(self, chatid, mon, tue, wed, thu, fri, sat, sun):
        query = 'INSERT INTO lessons VALUES ({}, "{}", "{}", "{}", ' \
                '"{}", "{}", "{}", "{}")'.format(chatid, mon, tue, wed, thu, fri, sat, sun)
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def insert_user(self, chat_id, email):
        query = 'INSERT INTO users VALUES ({}, "{}")'.format(chat_id, email)
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def search_lessons_chatid(self, chat_id):
        query = 'SELECT Mon, Tue, Wed, Thu, Fri, Sat, Sun FROM lessons WHERE chat_id="{}"'.format(chat_id)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_lessons(self, chat_id):
        query = 'DELETE FROM lessons WHERE chat_id="{}"'.format(chat_id)
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def delete_user(self, chat_id):
        query = 'DELETE FROM users WHERE chat_id="{}"'.format(chat_id)
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def search_all(self, table):
        query = 'SELECT * FROM {}'.format(table)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_user_chatid(self, chatid):
        query = 'SELECT * FROM users WHERE chat_id="{}"'.format(chatid)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_schedule(self, column, lesson, chat_id):
        query = 'UPDATE lessons SET {}="{}" WHERE chat_id={}'.format(column, lesson, chat_id)
        self.cursor.execute(query)
        self.connection.commit()

    def lessons_dayofweek(self, day, chat_id):
        query = 'SELECT {} FROM lessons WHERE chat_id="{}"'.format(day, chat_id)
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def close_conn(self):
        self.connection.close()


days_rus = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

days = {'Пн': 'Mon', 'Вт': 'Tue', 'Ср': 'Wed', 'Чт': 'Thu', 'Пт': 'Fri', 'Сб': 'Sat', 'Вс': 'Sun'}

lessons_number = {'09:00': '1 пара', '10:30': '2 пара', '12:10': '3 пара',
                  '13:40': '4 пара', '15:10': '5 пара', '16:40': '6 пара',
                  '18:10': '7 пара', '19:40': '8 пара',
                  '15:20': '5 пара', '16:50': '6 пара', '14:10': '5 пара', '15:40': '5 пара', '19:00': '8 пара',
                  '08:40': '1 пара', '09:30': '1 пара', '11:10': '2 пара', '12:40': '3 пара', '14:20': '5 пара',
                  '15:50': '6 пара', '10:00': '2 пара', '15:00': '5 пара', '12:00': '3 пара', '10:35': '2 пара',
                  '16:00': '6 пара', '17:10': '6 7 пара', '18:20': '7 пара', '19:50': '8 пара'}


def addition_days(n):
    addition_days = str(datetime.datetime.now() + datetime.timedelta(days=n))[:10]
    return addition_days.replace('-', '.')


def parsing_lessons(schedule, upd_type='week'):
    d = json.loads(schedule)
    if d != []:
        lessons = []
        for day in days_rus:
            schedule_lessons = ''
            if d['Lessons'] is None:
                continue
            for lesson in d['Lessons']:
                if lesson['dayOfWeekString'] == day:
                    if lesson['beginLesson'] in lessons_number:
                        schedule_lessons += lessons_number[lesson['beginLesson']] + '\r\n' + lesson['kindOfWork'] + '\r\n' + lesson['lecturer'] + '\r\n' + lesson['discipline'] + '\r\n' + \
                                            lesson['beginLesson'] + '-' + lesson['endLesson'] + '\r\n'
                    else:
                        schedule_lessons += lesson['kindOfWork'] + '\r\n' + lesson['lecturer'] + '\r\n' + lesson['discipline'] + '\r\n' + \
                                            lesson['beginLesson'] + '-' + lesson['endLesson'] + '\r\n'

                    if lesson.get('building'):
                        schedule_lessons += lesson['building'] + '\r\n~~~~~~~~~~~~~\r\n'
                    if lesson.get('auditorium'):
                        schedule_lessons += lesson['auditorium'] + '\r\n'

            schedule_lessons = re.sub('[\\\\"]', '', schedule_lessons)
            if upd_type == 'week':
                if schedule_lessons == '':
                    lessons.append((day, 'Нет пар'))
                    continue
                else:
                    lessons.append((day, schedule_lessons.replace('\\', '')))

        return lessons
    return False


@retry(stop_max_attempt_number=3)
def downlaod_html(urls):
    for _ in range(3):
        page = requests.get(urls[0]).content.decode('utf8')
        if page:
            html = parsing_lessons(page)
            if html is not False:
                for day, schedule in html:
                    mysql = MYSQL()
                    mysql.update_schedule(days[day], schedule, urls[2])
                    mysql.close_conn()
            print('Проапдейтил {}'.format(urls[1]))
            break


def collect_urls(from_date, to_date):
    urls = []
    mysql = MYSQL()
    for _id, chat_id, email, dt in mysql.search_all('users'):
        url = 'http://92.242.58.221/ruzservice.svc/v2/' \
              'personlessons?fromdate={}&todate={}&email={}'.format(from_date, to_date, email)
        urls.append((url, email, chat_id))
    mysql.close_conn()
    print('Собрал все ссылки')
    return urls


def run_upd():
    c = 0
    for data in collect_urls(addition_days(0), addition_days(6)):
        threading.Thread(target=downlaod_html, args=(data,)).start()
        c += 1
        if c == 20:
            time.sleep(3)
            c = 0
    print('done')

run_upd()
