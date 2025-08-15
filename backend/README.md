# StyleGhor Backend

A Django-based e-commerce backend API.

## Deployment on Render

### Prerequisites
- Render account
- Git repository with your code

### Steps

1. **Connect your repository to Render**
   - Go to [render.com](https://render.com)
   - Create a new Web Service
   - Connect your GitHub/GitLab repository
   - Select the `backend` directory as the root directory

2. **Environment Variables**
   Set these environment variables in Render:
   - `SECRET_KEY`: A secure Django secret key
   - `DEBUG`: Set to `false` for production
   - `ALLOWED_HOSTS`: Your Render domain (e.g., `your-app.onrender.com`)
   - `DATABASE_URL`: Will be automatically set by Render

3. **Build & Deploy**
   - Render will automatically use the `build.sh` script
   - The service will start with `gunicorn styleghor.wsgi:application`

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Project Structure
- `styleghor/`: Main Django project settings
- `shop/`: E-commerce app
- `users/`: Custom user management app
- `requirements.txt`: Python dependencies
- `render.yaml`: Render deployment configuration
- `build.sh`: Build script for deployment