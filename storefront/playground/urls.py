# map to the view function

from django.urls import path
from  . import views

#URLConf
urlpatterns = [
    path('hello/', views.say_hello)

]
#no input, so we just use reference