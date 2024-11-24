# CertVerif - Certificate Verification System

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-beta-orange)
![Last Commit](https://img.shields.io/github/last-commit/AntiSecTech/CertVerif)
![Languages](https://img.shields.io/github/languages/count/AntiSecTech/CertVerif)
![Top Language](https://img.shields.io/github/languages/top/AntiSecTech/CertVerif)

A robust certificate verification system built with Python, offering both public verification capabilities and administrative management of certificates.

## 🚀 Tech Stack

- **Backend**: Python
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Storage**: JSON-based
- **UI Framework**: Material Design

## ✨ Key Features

### 🌐 Public Interface

- Certificate verification via unique number
- QR code integration for quick verification
- Mobile-responsive design
- Real-time status checking
- Detailed certificate information display

### 👑 Admin Dashboard

- Secure authentication system
- Real-time statistics and metrics
- Complete certificate lifecycle management
- Administrator account control
- Role-based access (Admin/User)

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- pip package manager

### Quick Start

```bash
# Clone repository
git clone https://github.com/AntiSecTech/CertVerif.git
cd CertVerif

# Install dependencies
pip install -r requirements.txt

# Start server
python app.py
```

## 🔑 Default Credentials

⚠️ **Important**: Please change these default credentials immediately after first login for security reasons!

### 👑 Admin Access

```yaml
 Username: admin
 Password: admin
```

### 👤 User Access

```yaml
Username: user
Password: user
```

⚠️ **Important**: Please change these default credentials immediately after first login for security reasons!

## 📁 Project Structure

```sh
CertVerif/
├── app.py              # Main application
├── create_admin.py     # Admin setup utility
├── data/               # Data storage
├── static/             # Assets
│   ├── css/            # Stylesheets
│   └── js/             # JavaScript modules
└── templates/          # HTML templates
```

## 🔒 Security Features

- Password hashing
- Session management
- Input validation
- Role-based authorization

## 📊 Data Structure

### Certificate Format

```json
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
```

## 🔄 Current Status

- ✅ Basic certificate management
- ✅ Admin interface
- ✅ Public verification
- ✅ QR code support
- 🚧 Email notifications (Planned)
- 🚧 Bulk operations (Planned)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/Enhancement`)
3. Commit changes (`git commit -m 'Add Enhancement'`)
4. Push to branch (`git push origin feature/Enhancement`)
5. Open Pull Request

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## 👤 Author

[@AntiSecTech](https://github.com/AntiSecTech)

---
⭐ Star this repository if you find it helpful!
