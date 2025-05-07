# Ram Naam Jaap Application

A digital platform for devotees to practice and track their "naam jaap" (repetition of Lord Ram's name), view statistics, and participate in a community of practitioners.

## Features

- User authentication with location tracking
- Real-time Ram Naam typing and counting
- Personal statistics and history tracking
- Target setting and achievement system
- Global and city-wise leaderboards
- Mobile-responsive design

## Tech Stack

- **Backend**: Django 5 with Python 3.12
- **Frontend**: 
  - Tailwind CSS for styling
  - Alpine.js for interactive UI components
  - HTMX for dynamic content without full page reloads
- **Templates**: Jinja2 (replacing Django's default templates)
- **Database**: PostgreSQL (both local development and production)
- **Caching**: Redis
- **Deployment**: Docker containers for easy deployment

## Prerequisites

- Python 3.12
- PostgreSQL
- Redis
- Node.js and npm (for Tailwind CSS)

## Local Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-username/ram-naam-jaap.git
cd ram-naam-jaap
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Install frontend dependencies**

```bash
npm install
```

5. **Configure PostgreSQL**

Create a database for the application:

```bash
sudo -u postgres psql
postgres=# CREATE DATABASE ram_naam_jaap;
postgres=# CREATE USER ram_user WITH PASSWORD 'your_password';
postgres=# ALTER ROLE ram_user SET client_encoding TO 'utf8';
postgres=# ALTER ROLE ram_user SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE ram_user SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE ram_naam_jaap TO ram_user;
postgres=# \q
```

6. **Configure Redis**

Ensure Redis server is running:

```bash
sudo systemctl start redis  # or redis-server
```

7. **Set up environment variables**

Create a `.env` file in the project root with the following content:

```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://ram_user:your_password@localhost:5432/ram_naam_jaap
REDIS_URL=redis://localhost:6379/0
```

8. **Run migrations**

```bash
python manage.py migrate
```

9. **Create a superuser**

```bash
python manage.py createsuperuser
```

10. **Start the development server**

```bash
python manage.py runserver
```

## Accessing the Application

- Main application: http://localhost:8000/
- Admin dashboard: http://localhost:8000/admin/
- Django admin: http://localhost:8000/durga/

## Production Deployment

For production deployment, follow these additional steps:

1. Configure `settings/production.py` with appropriate values
2. Set up Nginx and Gunicorn
3. Configure SSL certificates
4. Set up database backups
5. Configure monitoring

Detailed deployment instructions can be found in the deployment documentation.

## Test Users

For testing purposes, you can use the test accounts provided in `test_users.txt`.

## Project Structure

The application follows a modular structure with separate Django apps for different functionality:

- `core`: Core application functionality and shared components
- `accounts`: User authentication and profile management
- `jaap`: Core naam jaap functionality
- `dashboard`: User dashboard and statistics
- `community`: Community features and leaderboards

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the spiritual practice of Ram Naam Jaap
- Thanks to all the devotees and contributors 