"""
WSGI config for DeBaser project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

python_home = '/home/juma/environments/my_env'

import os
import time
import sys
import traceback
import signal
import site


python_version = '.'.join(map(str, sys.version_info[:2]))
site_packages = python_home + '/lib/python%s/site-packages' % python_version
site.addsitedir(site_packages)

# Remember original sys.path.
prev_sys_path = list(sys.path)

# Add the site-packages directory.
#site.addsitedir(site_packages)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)

sys.path[:0] = new_sys_path


sys.path.append('/home/juma/IITA_PROJECTS')
sys.path.append('/home/juma/IITA_PROJECTS/DeBaser')
sys.path.append('/home/juma/IITA_PROJECTS/DeBaser/DeBaser')


os.environ['PYTHON_EGG_CACHE'] = '/tmp'
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DeBaser.settings")
os.environ['DJANGO_SETTINGS_MODULE'] = 'DeBaser.settings'

from django.core.wsgi import get_wsgi_application
#try:
#    application = get_wsgi_application()
#    print ('WSGI without exception')
#except Exception:
#    print ('handling WSGI exception')
#    # Error loading applications.                                                                                                                            
#    if 'mod_wsgi' in sys.modules:
#        traceback.print_exc()
#        os.kill(os.getpid(), signal.SIGINT)
#        time.sleep(2.5)



application = get_wsgi_application()
#application = django.core.handlers.wsgi.WSGIHandler()


