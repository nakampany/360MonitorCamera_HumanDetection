from django.urls import path
from . import views

app_name = 'monitercamera'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('camera/', views.CameraView.as_view(), name="camera"),
    path('camera_photo/', views.CameraPhotoView.as_view(), name="camera_photo"),
]