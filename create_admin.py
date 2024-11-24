from werkzeug.security import generate_password_hash
import json
import os

# Create admin credentials
admin_data = {
    "administrators": [
        {
            "username": "admin",
            "password_hash": generate_password_hash("admin"),  # Change this password
            "role": "superadmin"
        }
    ]
}

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Write to admin.json
with open('data/admin.json', 'w') as f:
    json.dump(admin_data, f, indent=4)

print("Admin configuration created successfully!")
print("Username: admin")
print("Password: admin")  # Change this if you changed it above 