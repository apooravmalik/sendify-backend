from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('file_transfer.urls')),  # Routes to your file_transfer app
]
