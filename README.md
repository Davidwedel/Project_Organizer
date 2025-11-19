# Project Organizer

A Flask-based web application for managing and organizing projects, tracking supplies, roadblocks, and collaboration.

## Features

- **Project Management**: Create, edit, and delete projects with customizable categories and types
- **Supply Tracking**: Maintain checklists of supplies needed for each project
- **Roadblock Tracking**: Document and track blockers with username attribution
- **Comments**: Add timestamped comments to projects
- **Help Wanted View**: See all roadblocks across projects in one place
- **Supplies Needed View**: View all supply needs across all projects
- **User Attribution**: Tracks usernames via Apache Basic Auth (falls back to 'Anonymous')

## Requirements

- Python 3.7+
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd projects
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5003`

## Deployment

### Apache with mod_wsgi

An example Apache configuration is provided in `apache-config.example`.

1. Install mod_wsgi:
```bash
# Fedora/RHEL
sudo dnf install python3-mod_wsgi

# Debian/Ubuntu
sudo apt install libapache2-mod-wsgi-py3
```

2. Copy and customize the Apache configuration:
```bash
cp apache-config.example /etc/httpd/conf.d/projects.conf
# Edit the configuration as needed
```

3. Restart Apache:
```bash
sudo systemctl restart httpd
```

## Database

The application uses SQLite and automatically creates the database at `instance/projects.db` on first run. Default project types (maintenance, new, repair, upgrade) are seeded automatically.

## Project Structure

```
.
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── wsgi.py               # WSGI entry point for production
├── requirements.txt       # Python dependencies
├── templates/            # Jinja2 templates
├── static/               # CSS and static assets
└── instance/             # Database storage (gitignored)
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
