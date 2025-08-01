import os
from app import create_app

# Get the environment from environment variable, default to development
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

# Set the template folder explicitly
app.template_folder = 'templates'

if __name__ == '__main__':
    app.run(port=8005) 