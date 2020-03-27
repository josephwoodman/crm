from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float
import os
from flask_marshmallow import Marshmallow
# define the flask app
# double underscore pronounced dunderscore
KubrickAPI = Flask(__name__)
# config settings for SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
# telling flask (sqlalchemy) where the database file will be stored/accessible to/from
KubrickAPI.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'kubes.db')
# configure marshmallow
ma = Marshmallow(KubrickAPI)
# initialise our database as a python object
db = SQLAlchemy(KubrickAPI)


@KubrickAPI.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Successfully Created!')


@KubrickAPI.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Successfully Dropped!')


# need to decorate the function with @
@KubrickAPI.route('/')
def home():
    return jsonify(data='Welcome to this Kubrick API')

# RESTful APIs - well documented in how to use it
# making another endpoint
# users/consumers of my api must provide a key=value pair
# in the format of:
# p=lastname i.e. p=bossino
# cohort=enum('DP','DE','DM')


@KubrickAPI.route('/people', methods=['POST'])
def people():
    name = request.form['lastname']
    # retrieve records from a database
    peopledata = People.query.filter_by(lname=name).first()
    result = people_schema.dump(peopledata)
    return jsonify(result)


@KubrickAPI.route('/addpeople', methods=['POST', 'GET'])
def addpeople():
    fn = request.form['firstname']
    ln = request.form['lastname']
    em = request.form['emailaddress']
    # insert the data into sqlite database
    new_people = People(fname=fn, lname=ln, email=em)
    db.session.add(new_people)
    db.session.commit()
    # result = successfailure flag
    # if insert successful then return result
    # else return result
    return jsonify(data='{} {} has been added to the database'.format(fn, ln)), 201


@KubrickAPI.route('/deletepeople', methods=['GET', 'POST'])
def deletepeople():
    name = request.form['lastname']
    deleteperson = People.query.filter_by(lname=name).first()
    if deleteperson:
        db.session.delete(deleteperson)
        db.session.commit()
        return jsonify(data='{} has been removed'.format(name))
    else:
        return jsonify(data='{} did not exist in the database'.format(name))


# in SQLAlchemy a Model is a table - we are creating the blueprint for our own table called People
class People(db.Model):
    __tablename__ = 'people'  # make a table called people
    id = Column(Integer, primary_key=True)
    fname = Column(String)
    lname = Column(String)
    email = Column(String, unique=True)


class PeopleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'fname', 'lname', 'email')


people_schema = PeopleSchema()
if __name__ == '__main__':
    KubrickAPI.run()