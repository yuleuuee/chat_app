from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name ='home'),
    path('login/',views.user_login,name ='login'),
    path('signup/',views.user_signup,name ='signup'),
    path('public/',views.public_page,name ='public'),
    path('logout/',views.user_logout,name ='logout'),
    path('delete_account/',views.delete_account,name ='delete_account'),
    path('change_password/',views.change_password,name ='change_password'),
    path('edit_profile/',views.edit_profile,name ='edit_profile'),

    path('profile/',views.user_profile,name ='profile'),
]
