# Deployment Guide

This guide will help you deploy your Flask CRM application to production.

## Prerequisites

- Python 3.11 or higher
- Git
- A deployment platform account (Heroku, Railway, Render, etc.)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd clients-crm
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask init-db
   flask create-admin
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## Production Deployment

### Environment Variables

Set these environment variables in your production environment:

- `FLASK_ENV=production`
- `FLASK_APP=wsgi.py`
- `SECRET_KEY=your-super-secret-key`
- `DATABASE_URL=your-database-url`

### Database Setup

For production, use a proper database like PostgreSQL or MySQL:

#### PostgreSQL (Recommended)
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary
```

Update `requirements.txt`:
```
psycopg2-binary==2.9.7
```

#### MySQL
```bash
# Install MySQL adapter
pip install mysqlclient
```

Update `requirements.txt`:
```
mysqlclient==2.1.1
```

### Deployment Platforms

#### Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-super-secret-key
   heroku config:set DATABASE_URL=your-database-url
   ```

5. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

6. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

7. **Initialize database**
   ```bash
   heroku run flask init-db
   heroku run flask create-admin
   ```

#### Railway

1. **Connect your GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push**

#### Render

1. **Connect your GitHub repository to Render**
2. **Set build command**: `pip install -r requirements.txt`
3. **Set start command**: `gunicorn wsgi:app`
4. **Set environment variables**
5. **Deploy**

### Security Considerations

1. **Change default admin credentials**
   - The default admin user is created with username `admin` and password `admin123`
   - Change these immediately after deployment

2. **Use strong secret keys**
   - Generate a strong secret key: `python -c "import secrets; print(secrets.token_hex(32))"`

3. **Enable HTTPS**
   - Most deployment platforms provide HTTPS by default
   - Ensure your application redirects HTTP to HTTPS

4. **Database security**
   - Use strong database passwords
   - Restrict database access to your application only

### Monitoring and Maintenance

1. **Set up logging**
   - Monitor application logs for errors
   - Set up log aggregation if needed

2. **Database backups**
   - Set up regular database backups
   - Test backup restoration procedures

3. **Performance monitoring**
   - Monitor application performance
   - Set up alerts for downtime

### Troubleshooting

#### Common Issues

1. **Database connection errors**
   - Check DATABASE_URL format
   - Ensure database is accessible from your deployment platform

2. **Import errors**
   - Ensure all dependencies are in requirements.txt
   - Check Python version compatibility

3. **Static files not loading**
   - Ensure templates are in the correct location
   - Check file permissions

#### Getting Help

- Check the application logs: `heroku logs --tail` (Heroku)
- Review deployment platform documentation
- Check Flask and extension documentation

## Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| DEBUG | True | False |
| SECRET_KEY | Simple key | Strong random key |
| Database | SQLite | PostgreSQL/MySQL |
| Server | Flask dev server | Gunicorn |
| HTTPS | No | Yes |

## Next Steps

After deployment:

1. Test all functionality
2. Change default admin credentials
3. Set up monitoring
4. Configure backups
5. Set up CI/CD pipeline 