from pymongo import MongoClient

MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)
db = client['bankserver']


'''
    Conexiones a BD
'''


def init_db():
    collections = db['clients']
    return collections


def users_db():
    collections = db['users']
    return collections


def administrators_db():
    collections = db['administrators']
    return collections


def transactions_db():
    collections = db['transactions']
    return collections

def auditors_db():
    collections = db['auditors']
    return collections    


def sobregiros_db():
    collections = db['overdraft']
    return collections


def retiros_db():
    collections = db['retiros']
    return collections