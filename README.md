# CertVerif - Certificate Verification System

CertVerif is a web-based certificate verification system that allows organizations to manage and verify digital certificates. It provides both a public verification interface and an administrative dashboard for certificate management.

![CertVerif Logo](/static/img/logo.png)

## Features

### Public Interface

- Certificate verification using certificate number and owner details
- QR code support for quick certificate verification
- Responsive design for mobile and desktop devices
- Real-time verification status display
- Detailed certificate information view

### Administrative Dashboard

- Secure admin login system
- Dashboard with key metrics:
  - Total certificates
  - Valid certificates
  - Expiring certificates (30-day warning)
  - Expired certificates
  - Certificate types
- Certificate Management:
  - Create new certificates
  - Edit existing certificates
  - Delete certificates
  - View all certificates with status indicators
- Administrator Management:
  - Create new admin accounts
  - Edit admin permissions
  - Delete admin accounts
  - Role-based access control (Admin/Super Admin)

### Technical Features

- RESTful API for certificate verification
- Secure session management
- Password hashing using Werkzeug
- JSON-based data storage
- CSRF protection
- Responsive UI using Material Design
- Modular JavaScript architecture

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

- Clone the repository:

```bash
git clone https://github.com/yourusername/certverif.git
cd certverif
```

- Install required packages:

```bash
pip install -r requirements.txt
```

- Create initial admin account:

```bash
python create_admin.py
```

- Create required directories:

```bash
mkdir -p data
```

### Configuration

- Default admin credentials:

  - Username: `admin`
  - Password: `admin`

**Important**: Change the default password after first login!

- Application configuration:

  - Port: 5000 (default)
  - Session timeout: 1 hour
  - Data storage: `data/` directory

## Usage

### Starting the Server

1. Start the main application:

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Accessing the System

- Public verification: `http://localhost:5000`
- Admin dashboard: `http://localhost:5000/admin/dashboard`
- API endpoint: `http://localhost:5000/api/verify/<cert_number>`

### API Usage

Verify a certificate via API:

```bash
curl -H "Accept: application/json" http://localhost:5000/api/verify/<cert_number>
```

## Project Structure

```sh
certverif/
├── app.py # Main application server
├── admin.py # Admin interface handler
├── create_admin.py # Admin account creation utility
├── data/
│ ├── admin.json # Admin user data
│ └── certificates.json# Certificate data
├── static/
│ ├── css/ # Stylesheets
│ │ ├── admin.css
│ │ ├── style.css
│ │ └── verify.css
│ └── js/ # JavaScript modules
│ ├── admin-form.js
│ ├── admins-list.js
│ ├── certificate-form.js
│ ├── certificates-list.js
│ └── main.js
├── templates/ # HTML templates
│ ├── admin_dashboard.html
│ ├── admin_form.html
│ ├── admin_login.html
│ ├── admins_list.html
│ ├── certificate_form.html
│ ├── certificates_list.html
│ ├── index.html
│ └── verify.html
└── requirements.txt # Python dependencies
```

## Security Features

- Password hashing using Werkzeug
- Secure session management
- CSRF protection
- HTTP-only cookies
- XSS protection
- Input validation
- Role-based access control

## Development

### JavaScript Modules

- `admin-form.js`: Admin user management
- `admins-list.js`: Admin list display and operations
- `certificate-form.js`: Certificate creation/editing
- `certificates-list.js`: Certificate list display and operations
- `main.js`: Public interface functionality

### Styling

- Material Design icons
- Responsive grid system
- Mobile-first approach
- Custom CSS variables for theming

## Data Structure

### Certificate JSON Structure

```json
{
    "certificates": [
        {
            "cert_number": "CV24-001-241121",
            "cert_type": {
                "type": "DC",
                "year": 2024,
                "number": 1,
                "title": "Example Certificate",
                "description": "API & Web Interface Testing Certificate"
            },
            "owner": "John Doe",
            "birthdate": "1990-01-01",
            "address": {
                "street": "Main St",
                "no": "123",
                "city": "City",
                "zip": "12345"
            },
            "contact": {
                "phone": "+1234567890",
                "email": "john.doe@example.com"
            },
            "expire_date": "2025-11-21",
            "is_valid": true
        }
    ]
}
```

### Admin JSON Structure

```json
{
    "administrators": [
        {
            "username": "admin",
            "password_hash": "hashed_password",
            "role": "superadmin"
        }
    ]
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Support

For support, please open an issue in the GitHub repository.

## Roadmap

- [ ] Add certificate template system
- [ ] Implement email notifications
- [ ] Add bulk certificate operations
- [ ] Enhance API functionality
- [ ] Add audit logging
- [ ] Add export/import functionality
- [ ] Implement certificate revocation system
- [ ] Add multi-language support

## Known Issues

- No built-in backup system for JSON data files
- Limited input validation on some fields

## Production Deployment

For production deployment, consider:

1. Using a proper database instead of JSON files
2. Implementing HTTPS
3. Setting up proper logging
4. Configuring backup systems
5. Implementing rate limiting
6. Setting up monitoring

## Requirements

See `requirements.txt` for Python package dependencies:

- Flask
- Flask-CORS
- Werkzeug

## Version History

- 0.1.0
  - Initial Release
  - Basic certificate management
  - Admin interface
  - Public verification
- 0.2.0

## Author

- [@AntiSecTech](https://github.com/antisectech)

## Acknowledgments

- [Material Design Icons](https://materialdesignicons.com/)
- [Flask framework](https://flask.palletsprojects.com/)
- [Werkzeug security](https://werkzeug.palletsprojects.com/)
- [Python community](https://www.python.org/)
