
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.page_login, name="login"),
    path('register/', views.register_user, name="register"),
    path('logout/', views.user_logout, name="logout"),
    path('profile/<str:pk>/', views.user_profile, name="profile"),
    path('edit-user/', views.edit_user, name="edit-user"),
     path('upload-profile-img/<str:pk>/', views.upload_profile_image, name='upload-profile-img'),


    path('', views.home, name="home"),

    path('topics/', views.topic_page, name="topics"),
    path('activity/', views.activity_page, name="activity"),

    path('room/<str:pk>/', views.room, name="room"),
    path('create-room/', views.create_room, name="create-room"),
    path('update-room/<str:pk>/', views.update_room, name="update-room"),
    path('delete-room/<str:pk>/', views.delete_room, name="delete-room"),
    path('delete-message/<str:pk>/', views.delete_message, name="delete-message"),
]