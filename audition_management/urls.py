from django.conf.urls import url
# from django.contrib import admin
from django.contrib.auth import views as auth_views
from audition_management import views


app_name = "audition_management"
urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='index'),
    url(r'^settings$', views.SettingsView.as_view(), name='settings')
    url(r'^role/$', views.RoleView.as_view(), name='role'),
    url(r'^create/$', views.RoleCreationView.as_view(), name='create'),
    # url(r'^admin/', admin.site.urls),

]
