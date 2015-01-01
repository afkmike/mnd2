from django.conf.urls import patterns, url

from home import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^index.htm', views.index, name='index'),
        url(r'gallery.htm',views.gallery,name='gallery'),
        url(r'services.htm',views.services,name='services'),
        url(r'contact.htm',views.contact,name='contact'),

        )
