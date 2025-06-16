from .base import *

# Importar settings específicos baseado no ambiente
import os
if os.environ.get('RAILWAY_ENVIRONMENT'):
    from .production import *
else:
    from .development import *