from flask import Flask, render_template
from flask_restful import Api, Resource, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fox_pol.db'
db = SQLAlchemy(app)
articles = Table('articles', db.metadata, autoload=True, autoload_with=db.engine)


@app.route("/")
def welcome():
    return render_template('welcome.html')


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


api.add_resource(SelectAll, '/all')

api.add_resource(Key, "/key/<string:field>/<string:keyword>")

api.add_resource(DateRange, "/daterange/<string:from_date>/<string:to_date>")

api.add_resource(KeyRange, "/keyrange/<string:from_date>/<string:to_date>/<string:field"
                           ">/<string:keyword>")

api.add_resource(Specific, "/specific/<string:column>/<string:from_date>/<string:to_date"
                           ">/<string:field>/<string:keyword>")

if __name__ == "__main__":
    app.run(debug=True)
# todo try marshal with and fields
