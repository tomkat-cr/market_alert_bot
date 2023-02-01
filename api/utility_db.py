from bson.json_util import dumps

from pymongo import MongoClient
from werkzeug.local import LocalProxy

from .settings import settings


# Database Low Level


def get_db():
    client = MongoClient(settings.DB_URI)
    return client.get_database(settings.DB_NAME)


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def test_connection():
    return dumps(db.list_collection_names())


def collection_stats(collection_nombre):
    return dumps(db.command('collstats', collection_nombre))


# Database High Level


def get_id_as_str(resultset):
    return str(resultset['_id'])


def verify_required_fields(fields, required_fields, error_code):
    resultset = dict({
        'error': False,
        'error_message': '',
        'resultset': dict()
    })
    for element in required_fields:
        if element not in fields:
            resultset['error_message'] = '{}{}{}'.format(
                resultset['error_message'],
                ', ' if resultset['error_message'] != '' else '',
                element
            )
    if resultset['error_message']:
        resultset['error_message'] = 'Missing mandatory elements:' + \
            f" {resultset['error_message']} [{error_code}]."
        resultset['error'] = True
    return resultset
