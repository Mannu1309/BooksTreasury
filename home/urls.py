from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name='home'),
    path('orders', views.orders, name='orders'),
    path('accountsetting/', views.accountsetting, name='accountsetting'),
    path("about", views.about, name='about'),
    path("contact", views.contact, name='contact'),
    path("book/<str:pk>/",views.viewBook, name='book'),
    path("sign_in",  views.sign_in, name='sign_in'),
    path("logout",   views.logoutUser, name='logout'),
    path("sell", views.sell, name='sell'),
    path("cart", views.cart, name='cart'),
    path("update_item/", views.updateItem, name='update_item'),
    path("checkout", views.checkout, name='checkout'),
    path("process_order/", views.proccessOrder, name='process_order'),
    path("misc/", views.misc, name='misc'),
    path("privacypolicy/", views.privacypolicy, name='privacypolicy'),
    path("termsandconditions/", views.terms, name='terms'),
    path("disclaimer/", views.disclaimer, name='disclaimer'),
    path('search/', views.search, name='search_result'),
    path('email_temp/', views.emailtemp, name='email_temp'),
    path('invoice/', views.invoice, name='invoice'),
    path('dark/', views.dark, name='dark'),
    path("like/<str:id>/", views.liked_video, name="like-book"),
    path("dislike/<str:id>/", views.dislike_video, name="dislike-book"),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), name="password_reset_complete"),
]   