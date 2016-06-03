from django.conf.urls import url
from . import main_views, canvas_views

urlpatterns = [
    url(r'^main$', main_views.index, name='main_index'),

    url(r'^canvas/schema/(?P<schema_id>[^/]+)$', canvas_views.schema, name='canvas_schema'),
    url(r'^canvas/schema/(?P<schema_id>[^/]+)/diff/(?P<other_schema_id>[^/]+)$', canvas_views.diff_schemas, name='diff_canvas_schemas'),
    url(r'^canvas/dump$', canvas_views.list_dumps, name='list_canvas_dumps'),
    url(r'^canvas/dump/(?P<dump_id>[^/]+)$', canvas_views.dump, name='canvas_dump'),
    url(r'^canvas/table/(?P<table_name>[^/]+)$', canvas_views.table, name='canvas_table'),
]
