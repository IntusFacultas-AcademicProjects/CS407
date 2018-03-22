from django.conf.urls import url
from audition_management import views


app_name = "audition_management"
urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='index'),
    url(r'^settings$', views.SettingsView.as_view(), name='settings'),
    url(r'^role/(?P<pk>[0-9+]+)$', views.RoleView.as_view(), name='role'),
    url(r'^create/(?P<pk>[0-9+]+)/tags/$', views.TagCreationView.as_view(),
        name="tags"),
    url(r'^create/$', views.RoleCreationView.as_view(), name='create'),
    url(r'^account/(?P<pk>[0-9]+)/$', views.AccountDelete.as_view(),
        name="delete-account"),
    url(r'^edit/(?P<pk>[0-9+]+)$',
        views.EditRoleView.as_view(), name='edit-role'),
    url(r'^user/(?P<pk>[0-9+]+)$', views.UserView.as_view(), name="user")
]
