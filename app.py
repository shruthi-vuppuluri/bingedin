"""
This is a compatibility file for Render.
It imports the WSGI application to satisfy the default Render deployment.
"""

from wsgi import application

# Alias the application for frameworks that look for this variable
app = application 