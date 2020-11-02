from bs4 import BeautifulSoup
import sqlite3
import requests
from datetime import datetime, timedelta


# noinspection PyUnboundLocalVariable
def insert_values(print_time_, topic_, headline_, summary_, url_):
    """
    a semi hard coded function to insert values into a db
    :param print_time_:
    :param topic_:
    :param headline_:
    :param summary_:
    :param url_:
    :return:
    """
    try:
        sqlite_connection = sqlite3.connect('fox_pol.db')
        cursor = sqlite_connection.cursor()

        sqlite_insert_with_param = """INSERT INTO articles (print_date, topic, 
        headline, summary, url) VALUES (date(?), ?, ?, ?, ?)"""

        data_tuple = (print_time_, topic_, headline_, summary_, url_)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqlite_connection.commit()
        print("Python Variables inserted successfully into sqlite table")

        cursor.close()

    except sqlite3.Error as sl_error:
        print("Failed to insert Python variable into sqlite table", sl_error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


#  opens a db connection creates a table and closes connection
db = sqlite3.connect('fox_pol.db')
db.execute("CREATE TABLE IF NOT EXISTS  articles (print_date DATE, "
           "topic VARCHAR(100), "
           "headline VARCHAR(100) UNIQUE, summary VARCHAR(100), url VARCHAR(100))")
db.close()
# initiates a text file
create_file = open(r'C:\Users\willi\PychamProjects\scraping\fox_pol.txt', 'w')
create_file.close()
# requests html and creates soup object
source = requests.get('https://www.foxnews.com/politics', timeout=20).text
soup = BeautifulSoup(source, 'lxml')
# finds all article lists
article_lists = soup.find_all("div", {"class": "content article-list"})
# searches for articles in article lists
for div_tag in article_lists:
    try:
        article_tags = div_tag.find_all("article")
        for tag in article_tags:
            #  ######## selectors bound to variables ########
            time_posted_raw = tag.find('span', class_='time').text
            if "mins" in time_posted_raw:
                min_time = int(time_posted_raw[0:2].zfill(2))
                U_time = (datetime.utcnow() - timedelta(minutes=min_time)).date()
            elif "just" in time_posted_raw:
                U_time = datetime.utcnow().date()
            else:
                hr_time = int(time_posted_raw[0:2].zfill(2))
                U_time = (datetime.utcnow() - timedelta(hours=hr_time)).date()
            topic = tag.find('span', class_='eyebrow').a.text
            headline = tag.find('h4', class_='title').a.text
            headline2 = tag.find('h4', class_='title').a
            url = "https://www.foxnews.com" + headline2['href']
            summary = tag.find('p', class_='dek').a.text
            # ########## variables inserted into db via function ##########
            insert_values(U_time, topic, headline, summary, url)
            # ########## variables written to text file #################
            with open(r'C:\Users\willi\PychamProjects\scraping\fox_pol.txt', 'r') as f:
                if headline not in f.read():
                    # noinspection PyAssignmentToLoopOrWithParameter
                    with open('fox_pol.txt', 'a+') as f:
                        print(U_time, file=f)
                        print(topic, file=f)
                        print(headline, file=f)
                        print(url, file=f)
                        print(summary, file=f)
                        print("=" * 20, file=f)
    except AttributeError as error:
        print("End of articles")
