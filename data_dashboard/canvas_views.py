from django.shortcuts import render
import canvas_api

def list_dumps(request):
    dumps = canvas_api.list_dumps()
    for d in dumps:
        d['megadump'] = d['numFiles'] == 1
    context = {'dumps': dumps}
    return render(request, 'data_dashboard/dumps.html', context)


def dump(request, dump_id):
    tables = []
    dump_data = canvas_api.dump_info(dump_id)
    for _, table in dump_data['artifactsByTable'].items():
        tables.append(table)
    tables.sort(key=lambda x: x['tableName'])
    context = {'dump': dump_data, 'tables': tables}
    return render(request, 'data_dashboard/dump.html', context)


def table(request, table_name):
    t = canvas_api.table_info(table_name)
    context = {'table': t}
    return render(request, 'data_dashboard/table.html', context)


def schema(request, schema_id):
    s1 = canvas_api.get_schema(schema_id)
    tables = []
    for _, table in s1['schema'].items():
        tables.append(table)
    tables.sort(key=lambda x: x['tableName'])
    schemas = [x['version'] for x in canvas_api.list_schemas()]
    schemas.sort(key=lambda s: [int(u) for u in s.split('.')])
    context = {'tables': tables, 'version': s1['version'], 'schemas': schemas}
    return render(request, 'data_dashboard/schema.html', context)


def diff_schemas(request, schema_id, other_schema_id):
    additions, deletions = canvas_api.diff_schemas(schema_id,
                                                   other_schema_id)
    tables = []
    for table in additions:
        for column in table['columns']:
            column['added'] = True
        t = {
            'tableName': table['tableName'],
            'columns': table['columns']
        }
        tables.append(t)
    for table in deletions:
        for column in table['columns']:
            column['added'] = False
        t = next((x for x in tables if x['tableName'] == table['tableName']),
                 None)
        if not t:
            t = {'tableName': table['tableName']}
            t['columns'] = []
            tables.append(t)
        t['columns'] += table['columns']
    tables.sort(key=lambda x: x['tableName'])

    context = {'s1': schema_id, 's2': other_schema_id, 'tables': tables}
    return render(request, 'data_dashboard/schema_diff.html', context)
