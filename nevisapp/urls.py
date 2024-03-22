from django.urls import path
from . import views

# SET THE NAMESPACE!
app_name = 'nevisapp'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('register/',views.register,name='register'),
    path('user_login/',views.user_login,name='user_login'),
    path('news_analysis/',views.news_analysis,name='news_analysis'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('news/',views.get_news, name='news'),
    path('news/<str:keywords>/', views.get_news_by_id, name='get_news_by_id'),
    path('aluminium/',views.import_and_return_json, name='aluminium'),
    path('al/',views.al_predict, name='al'),
    path('al_pred/',views.get_pred_al, name='al_pred'),
    path('al_pred_api/',views.get_data_from_api, name='al_pred_api'),
    path('coba/', views.coba, name='coba'),
]
