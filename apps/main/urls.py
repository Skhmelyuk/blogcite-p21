from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.post_list, name="post_list"),
    path('category/<slug:category_slug>', views.post_list, name="post_list_by_category"),
    path('post/<int:id>/<slug:slug>', views.post_detail, name="post_detail"),
]