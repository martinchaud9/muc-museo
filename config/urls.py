from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from analitica.views import estadisticas

urlpatterns = [
    path('admin/estadisticas/', estadisticas, name='estadisticas'),
    path('admin/', admin.site.urls),
    path('analitica/', include('analitica.urls')),
    path('', include('museo.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
