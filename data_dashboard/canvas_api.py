import hashlib
import base64
import hmac
from email.utils import formatdate
import requests
from django.conf import settings


def api_call(path):
    host = settings.CANVAS_DATA_HOST
    key = settings.CANVAS_DATA_KEY
    secret = settings.CANVAS_DATA_SECRET
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    method = 'GET'
    content_type = ''
    md5 = ''
    query_params = ''
    message = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        method, host, content_type, md5, path, query_params, date, secret
    )
    signature = base64.b64encode(
        hmac.new(bytes(secret, 'utf-8'), bytes(message, 'utf-8'), hashlib.sha256).digest()
    )

    signature = signature.decode('utf-8')

    url = "https://{}{}".format(host, path)
    headers = {
        'Authorization': "HMACAuth {}:{}".format(key, signature),
        'Date': date
    }
    r = requests.get(url, headers=headers)
    print("{}".format(r))
    return r.json()


def list_dumps():
    return api_call("/api/account/self/dump")


def latest_dump():
    return scrub_urls(api_call("/api/account/self/file/latest"))


def dump_info(dump_id):
    return scrub_urls(api_call("/api/account/self/file/byDump/{}".format(dump_id)))


def table_info(table_name):
    return api_call("/api/account/self/file/byTable/{}".format(table_name))


def list_schemas():
    return api_call("/api/schema")


def get_schema(schema_id='latest'):
    return api_call("/api/schema/{}".format(schema_id))


def diff_schemas(version1, version2='latest'):
    s1 = get_schema(version1)
    s2 = get_schema(version2)
    additions = get_schema_additions(s2, s1)
    deletions = get_schema_additions(s1, s2)
    return additions, deletions


def get_schema_additions(s1, s2):
    additions = []
    for table_name in get_table_names(s1):
        if get_table_by_name(s2, table_name):
            table_additions = get_table_additions(
                table_name,
                get_table_by_name(s1, table_name),
                get_table_by_name(s2, table_name)
            )
            if table_additions:
                additions.append(table_additions)
        else:
            additions.append(get_table_by_name(s1, table_name))
    return additions


def get_table_additions(table_name, t1, t2):
    columns = []
    t2_cols = {}
    for column in t2['columns']:
        t2_cols[column['name']] = column

    for column in t1['columns']:
        if not compare_columns(column, t2_cols):
            columns.append(column)
    if columns:
        return {'columns': columns, 'tableName': table_name}
    return None


def compare_columns(column, t2_cols):
    if column['name'] in t2_cols:
        c2 = t2_cols[column['name']]
        return (
            c2.get('description', None) == column.get('description', None) and
            c2.get('type', None) == column.get('type', None) and
            c2.get('length', None) == column.get('length', None)
        )
    return False


def get_table_names(schema):
    names = []
    for key, table in list(schema['schema'].items()):
        names.append(table['tableName'])
    names.sort()
    return names


def get_table_by_name(schema, name):
    return next(
        (y for x, y in list(schema['schema'].items()) if y['tableName'] == name),
        None)


def scrub_urls(dump):
    for table in dump['artifactsByTable']:
        for f in dump['artifactsByTable'][table]['files']:
            del f['url']
    return dump
