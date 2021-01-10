from flask import Flask, render_template, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from stop_words import stop_words

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fox_pol.db'
db = SQLAlchemy(app)
articles = Table('articles', db.metadata, autoload=True, autoload_with=db.engine)


@app.route("/")
def welcome():
    return render_template('welcome.html')


@app.route("/q")
def q():
    """
    a page that displays the result of a db query based on a query string in the url
    :return: JSON repr of DB search or 200 message
    """
    qstring = request.args
    arts = run_query(qstring)
    if arts:
        return arts
    return "No results, check query or broaden search", 200


def run_query(qstring):
    """
    parses a qstring from url for keywords then searches underlying db by combination of dates and topic.
    unspecified values default to be maximally inclusive
    :param qstring: query string passed from page calling the function
    :return: JSON
    """
    # parse qstring looking for key words for query
    if 'fromdate' in qstring:
        fromdate = qstring['fromdate']
    if 'fromdate' not in qstring:
        fromdate = "2020-01-01"
    if "todate" in qstring:
        todate = qstring["todate"]
    if 'todate' not in qstring:
        todate = "2100-01-01"
    if "value" in qstring:
        value = qstring["value"]
    if 'value' not in qstring:
        value = " "
    # coerce variable to string format for compatibility with db
    fromdate, todate, value = str(fromdate), str(todate), str(value)
    # sanitize query inputs
    if '%' or ';' in value:
        value = value.replace('%', '')
        value = value.replace(';', '')
    # wrap 'like' search in modulo
    value = "%" + value + "%"
    # init empty dictionary/obj
    article_dict = {}
    # init a counter for naming article objects
    count = 1
    # define query
    query = f"SELECT * FROM articles WHERE print_date BETWEEN ? AND ? AND headline LIKE ?"
    # create input tuple to be passed to db driver
    input_tuple = (fromdate, todate, value)
    # execute query with inputs and capture as iterable
    q_result_set = db.engine.execute(query, input_tuple)
    # fetch all from iterable
    q_results = q_result_set.fetchall()
    # loop over iterable serializing rows of db into dict/object
    for r in q_results:
        article = {'date': str(r.print_date), 'topic': r.topic, 'headline': r.headline,
                   'summary': r.summary, 'url': r.url}
        # article object is set to value of numeric key within collection of articles
        article_dict[count] = article
        # numeric key autoincrement
        count += 1
        # return collection of articles as object containing numeric keys who's values are objects representing articles
    return article_dict


def select_all():
    article_dict = {}
    count = 1
    results = db.session.query(articles).all()
    for r in results:
        article = {'date': str(r.print_date), 'topic': r.topic, 'headline': r.headline,
                   'summary': r.summary, 'url': r.url}
        article_dict[count] = article
        count += 1
    return article_dict


def key(field, keyword):
    article_dict = {}
    count = 1
    query = f"SELECT * FROM articles WHERE {field} LIKE ?"
    new_keyword = str(keyword)
    if '%' or ';' in new_keyword:
        new_keyword.replace('%;', '')
    like_keyword = "%" + new_keyword + "%"
    input_tuple = (like_keyword,)
    q_result_set = db.engine.execute(query, input_tuple)
    q_results = q_result_set.fetchall()
    for r in q_results:
        article = {'date': str(r.print_date), 'topic': r.topic, 'headline': r.headline,
                   'summary': r.summary, 'url': r.url}
        article_dict[count] = article
        count += 1
    return article_dict


def date_range(from_date, to_date):
    article_dict = {}
    count = 1
    query = f"SELECT * FROM articles WHERE print_date BETWEEN ? AND ?"
    input_tuple = (from_date, to_date)
    q_result_set = db.engine.execute(query, input_tuple)
    q_results = q_result_set.fetchall()
    for r in q_results:
        article = {'date': str(r.print_date), 'topic': r.topic, 'headline': r.headline,
                   'summary': r.summary, 'url': r.url}
        article_dict[count] = article
        count += 1
    return article_dict


def key_range(from_date, to_date, field, keyword):
    article_dict = {}
    count = 1
    query = f"SELECT * FROM articles WHERE print_date BETWEEN ? AND ? AND {field} LIKE ?"
    new_keyword = str(keyword)
    if '%' in new_keyword:
        new_keyword.replace('%', '')
    like_keyword = "%" + new_keyword + "%"
    input_tuple = (from_date, to_date, like_keyword)
    q_result_set = db.engine.execute(query, input_tuple)
    q_results = q_result_set.fetchall()
    for r in q_results:
        article = {'date': str(r.print_date), 'topic': r.topic, 'headline': r.headline,
                   'summary': r.summary, 'url': r.url}
        article_dict[count] = article
        count += 1
    return article_dict


def specific(column, from_date, to_date, field, keyword):
    article_dict = {}
    count = 1
    query = f"SELECT {column} FROM articles WHERE print_date BETWEEN ? AND ? AND" \
            f" {field} LIKE ?"
    new_keyword = str(keyword)
    if '%' in new_keyword:
        new_keyword.replace('%', '')
    like_keyword = "%" + new_keyword + "%"
    input_tuple = (from_date, to_date, like_keyword)
    q_result_set = db.engine.execute(query, input_tuple)
    q_results = q_result_set.fetchall()
    for r in q_results:
        article = {}
        if "print_date" in column:
            article['print_date'] = str(r.print_date)
        if "topic" in column:
            article['topic'] = str(r.topic)
        if "headline" in column:
            article['headline'] = str(r.headline)
        if "summary" in column:
            article['summary'] = str(r.summary)
        if "url" in column:
            article['url'] = str(r.url)
        article_dict[count] = article
        count += 1

    return article_dict


def cloud(json):
    word_cloud = WordCloud(stopwords=stop_words, max_words=100,
                           background_color="white").generate(text_blob(json))
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def text_blob(json):
    string_blob = ""
    for each in json:
        try:
            url = json[each]["url"]
            source = requests.get(url, timeout=3).text
            soup = BeautifulSoup(source, 'lxml')
            article_string = soup.find("div", class_='article-body').text
            string_blob += article_string
        except:  # todo dont leave bare exception
            continue
    return string_blob



class SelectAll(Resource):
    def get(self):
        return select_all()


class Key(Resource):
    def get(self, field, keyword):
        return key(field, keyword)


class DateRange(Resource):
    def get(self, from_date, to_date):
        return date_range(from_date, to_date)


class KeyRange(Resource):
    def get(self, from_date, to_date, field, keyword):
        return key_range(from_date, to_date, field, keyword)


class Specific(Resource):
    def get(self, column, from_date, to_date, field, keyword):
        return specific(column, from_date, to_date, field, keyword)


class KeyCloud(Resource):
    def get(self, field, keyword):
        return cloud(key(field, keyword))


class DateRangeCloud(Resource):
    def get(self, from_date, to_date):
        return cloud(date_range(from_date, to_date))


class KeyRangeCloud(Resource):
    def get(self, from_date, to_date, field, keyword):
        return cloud(key_range(from_date, to_date, field, keyword))


# api.add_resource(Q, '/q')

api.add_resource(SelectAll, '/all')

api.add_resource(Key, "/key/<string:field>/<string:keyword>")

api.add_resource(DateRange, "/daterange/<string:from_date>/<string:to_date>")

api.add_resource(KeyRange, "/keyrange/<string:from_date>/<string:to_date>/<string:field"
                           ">/<string:keyword>")

api.add_resource(Specific, "/specific/<string:column>/<string:from_date>/<string:to_date"
                           ">/<string:field>/<string:keyword>")

api.add_resource(KeyCloud, "/key/<string:field>/<string:keyword>/cloud")

api.add_resource(DateRangeCloud, "/daterange/<string:from_date>/<string:to_date>/cloud")

api.add_resource(KeyRangeCloud, "/keyrange/<string:from_date>/<string:to_date>/<string"
                                ":field>/<string:keyword>/cloud")

if __name__ == "__main__":
    app.run(debug=True)

# todo find how to render a matplot as in a browser rather than in tkinter and redirect
#  to it
