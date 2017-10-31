
from django.conf.urls import url
from easy_admin import views


urlpatterns = [
    url(r'^$', views.index,name="table_index"),
    url(r'^(\w+)/(\w+)$', views.display_table_objs,name="table_objs"),
    url(r'^(\w+)/$',views.menus_url_jump,name="menus_url"),
    url(r'^(\w+)/(\w+)/(\w+)/change/$',views.table_obj_change,name="menus_url"),
    url(r'^(\w+)/(\w+)/(\d+)/delete/$', views.table_obj_delete,name="obj_delete"),
    url(r'^(\w+)/(\w+)/add/$', views.table_obj_add,name="table_obj_add"),
    url(r'^(\w+)/(\w+)/(\d+)/change/password/$', views.password_reset, name="password_reset"),
]
