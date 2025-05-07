# Ram Naam Jaap Application

A comprehensive spiritual platform for tracking devotional practice, viewing statistics, and participating in the community of Ram Naam Jaap practitioners.

## Project Overview

Ram Naam Jaap is built using Django 5 with a multi-application architecture that allows different components to run as independent services while maintaining a unified user experience. The platform uses Jinja2 as the primary template engine for frontend templates, with Django's built-in templates reserved for the admin interface.

## Core Features

- **Jaap Counter**: Track your devotional practice sessions
- **Statistics and Analytics**: View your progress and achievements
- **Community**: Connect with other practitioners, join forums and groups
- **Admin Dashboard**: Comprehensive admin tools for system management
- **Blog**: Read and share spiritual content

## Technical Architecture

### Multiple Application Structure

The platform is structured as multiple interconnected Django applications, each capable of running independently:

1. **Base Application** (Port 8000): Main user-facing application
2. **Admin Dashboard** (Port 8001): Custom admin interface
3. **API Service** (Port 8002): RESTful API for integrations
4. **Blog Platform** (Port 8003): Content management
5. **Community Platform** (Port 8004): User forums and discussions

## Setup and Installation

### Prerequisites

- Python 3.12
- PostgreSQL
- Redis (optional, falls back to in-memory cache)

### Installation Steps

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ram_naam_jaap.git
   cd ram_naam_jaap
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgres://postgres:postgres@localhost:5432/ram_naam_jaap
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. Setup the database:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Start the server using the Durga script:
   ```
   python durga.py
   ```

## Using the Durga Script

The `durga.py` script is a utility for managing development tasks. It provides a command-line interface with several useful features:

### Basic Usage

```
python durga.py [options]
```

### Options

- `--app` - Specify which app to run (main, admin, api, blog, community, all)
- `--port` - Specify the port to run the server on
- `--skip-cache` - Skip cache clearing
- `--skip-static` - Skip static file collection
- `--create-test-data` - Create test data
- `--check-jinja` - Check Jinja2 setup

### Examples

Start the main application:
```
python durga.py
```

Start the admin dashboard:
```
python durga.py --app admin
```

Start all applications:
```
python durga.py --app all
```

Start the main application on a custom port:
```
python durga.py --port 8080
```

## Jinja2 Templates

This project uses Jinja2 as the primary template engine, with Django's built-in templates reserved for the admin interface.

### Template Structure

- All Jinja2 templates use the `.jinja` extension
- Base templates are in `ram_naam_jaap/templates/`
- App-specific templates are in their respective directories

### Template Usage

Jinja2 provides several advantages including better performance and a more flexible syntax. The project includes helpful globals and filters:

- `url()` - Generate URLs using Django's URL system
- `static()` - Link to static files with automatic cache-busting
- `csrf_input()` - Generate CSRF tokens for forms
- `hasattr()` - Check if an object has an attribute

Example usage in templates:
```html
<!-- Link to a URL -->
<a href="{{ url('jaap:home') }}">Home</a>

<!-- Include a static file with cache-busting -->
<link href="{{ static('css/style.css') }}" rel="stylesheet">

<!-- Add CSRF protection to a form -->
<form method="post">
  {{ csrf_input(request) }}
  <!-- form fields -->
</form>
```

## Frontend Framework

- **Tailwind CSS** (via CDN) for styling
- **Alpine.js** (via CDN) for interactive UI components

## Deployment

The application can be deployed in two ways:

### Single-Server Deployment

For simpler setups, all components can run on a single server with Nginx used for routing based on paths:
- Main app: `example.com/`
- Admin dashboard: `example.com/admin/`
- API: `example.com/api/`

### Multi-Server Deployment

For larger installations, each component can run on separate servers/containers:
- Main app: `example.com`
- Admin dashboard: `admin.example.com`
- API: `api.example.com`
- Blog: `blog.example.com`
- Community: `community.example.com`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the spiritual practice of Ram Naam Jaap
- Thanks to all the devotees and contributors

## New Development Helper Scripts

We've added new helper scripts to improve the development workflow:

1. **ramjaap.sh**: A comprehensive shell script for project management
   ```bash
   ./ramjaap.sh [command]  # Run a command (try ./ramjaap.sh help)
   ```

2. **durga.py with command arguments**: Enhanced with command-line options
   ```bash
   python durga.py [all|clearcache|collectstatic|runserver]
   ```

3. **Shell aliases** (in .zshrc):
   ```bash
   rj [command]      # Short alias for ./ramjaap.sh
   ramjaap [command] # Alias for ./ramjaap.sh
   durga [command]   # Alias for python durga.py
   ```

See [README_HELPERS.md](README_HELPERS.md) for detailed documentation.

## Cache Busting

Static files now include automatic cache-busting to ensure browsers always load the latest assets. # jaapram
