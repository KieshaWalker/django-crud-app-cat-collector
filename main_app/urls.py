from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('home/', views.homeTwo, name='home'),
    path('about/', views.about, name='about'),
    path('cats/', views.cat_index, name='cat-index'),
    path('cats/<int:cat_id>/', views.cat_detail, name='cat-detail'),
    path('cats/create/', views.CatCreate.as_view(), name='cat-create'),
    path('cats/<int:pk>/update/', views.CatUpdate.as_view(), name='cat-update'),
    path('cats/<int:pk>/delete/', views.CatDelete.as_view(), name='cat-delete'),
    path(
        'cats/<int:cat_id>/add_feeding/', 
        views.add_feeding, 
        name='add_feeding'
    ),
    path('toys/create/', views.ToyCreate.as_view(), name='toy-create'),
    path('toys/<int:pk>/', views.toy_detail, name='toy-detail'),
    path('toys/', views.ToyList.as_view(), name='toy-index'),
    path('accounts/signup/', views.signup, name='signup'),
]