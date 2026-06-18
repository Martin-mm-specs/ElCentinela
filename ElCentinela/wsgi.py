import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElCentinela.settings')

application = get_wsgi_application()

# Añade esta línea para Vercel
app = application