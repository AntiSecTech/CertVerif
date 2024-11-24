#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import urllib.parse
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from http.cookies import SimpleCookie
import secrets
import time

class CertHandler(BaseHTTPRequestHandler):
    # Class-level session storage
    sessions = {}
    
    def generate_cert_number(self, cert_type_year, cert_type_number, issue_date):
        """Generate certificate number in format: CV24-001-241121"""
        year_suffix = str(cert_type_year)[-2:]  # Get last 2 digits of year
        number_formatted = f"{cert_type_number:03d}"  # Format number as 3 digits with leading zeros
        date_formatted = issue_date.strftime("%y%m%d")  # Format date as YYMMDD
        return f"CV{year_suffix}-{number_formatted}-{date_formatted}"

    def get_session(self):
        cookie = SimpleCookie(self.headers.get('Cookie'))
        session_id = cookie.get('session_id')
        if session_id:
            session = self.sessions.get(session_id.value)
            if session and session['expires'] > time.time():
                return session
        return None

    def create_session(self, admin_data):
        session_id = secrets.token_urlsafe(32)
        session = {
            'id': session_id,
            'username': admin_data['username'],
            'role': admin_data['role'],
            'expires': time.time() + 3600,  # 1 hour expiry
        }
        self.sessions[session_id] = session
        
        # Set secure cookie
        cookie = SimpleCookie()
        cookie['session_id'] = session_id
        cookie['session_id']['httponly'] = True
        cookie['session_id']['secure'] = True  # Enable in production
        cookie['session_id']['samesite'] = 'Strict'
        cookie['session_id']['path'] = '/'
        return cookie

    def require_auth(self):
        session = self.get_session()
        if not session:
            self.send_response(302)
            self.send_header('Location', '/admin/login')
            self.end_headers()
            return False
        return True

    def serve_file(self, path, content_type):
        try:
            with open(path, 'rb') as file:
                content = file.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)

    def load_template(self, template_name):
        with open(f'templates/{template_name}', 'r') as file:
            return file.read()

    def generate_verification_html(self, cert_data, status):
        template = self.load_template('verify.html')
        
        if status == 'valid':
            icon = "verified"
            message = "Valid Certificate"
            status_class = "valid"
        elif status == 'expired':
            icon = "warning"
            message = "Certificate Expired"
            status_class = "expired"
        else:
            icon = "error"
            message = "Invalid Certificate"
            status_class = "invalid"

        content = f'''
            <div class="icon material-icons {status_class}">{icon}</div>
            <div class="message">{message}</div>
        '''
        
        if cert_data:
            formatted_json = json.dumps(cert_data, indent=2)
            content += f'''
                <div class="data-container">
                    <div class="scroll-container">
                        <pre><code class="language-json">{formatted_json}</code></pre>
                    </div>
                </div>
            '''
            
        return template.replace('{{CONTENT}}', content)

    def verify_certificate(self, cert_number, last_name=None, first_name=None):
        try:
            with open('data/certificates.json', 'r') as file:
                data = json.load(file)
            
            for cert in data['certificates']:
                if cert['cert_number'] == cert_number:
                    # If names are provided, verify them
                    if last_name and first_name:
                        cert_last_name = cert['owner'].split()[-1].lower()
                        cert_first_name = cert['owner'].split()[0].lower()
                        if cert_last_name != last_name.lower() or cert_first_name != first_name.lower():
                            return {
                                'found': False,
                                'valid': False,
                                'status': 'invalid',
                                'message': 'Name does not match certificate owner'
                            }
                    
                    valid = datetime.strptime(cert['expire_date'], '%Y-%m-%d') > datetime.now()
                    return {
                        'found': True,
                        'valid': valid,
                        'status': 'valid' if valid else 'expired',
                        'data': cert if valid else {
                            'message': 'Certificate has expired',
                            'cert_number': cert['cert_number'],
                            'expire_date': cert['expire_date']
                        }
                    }
            
            return {
                'found': False,
                'valid': False,
                'status': 'invalid',
                'message': 'Certificate not found'
            }
        except Exception as e:
            return {
                'found': False,
                'valid': False,
                'status': 'invalid',
                'message': f'Error: {str(e)}'
            }

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        cookie = SimpleCookie()
        cookie['session_id'] = ''
        cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        cookie['session_id']['path'] = '/'
        return cookie

    def check_admin_permission(self):
        """Check if the current user has admin privileges"""
        session = self.get_session()
        if not session or session['role'] != 'admin':
            self.show_error_page('You do not have permission to access this page')
            return False
        return True

    def do_GET(self):
        # Public routes
        if self.path == '/admin/login':
            content = self.load_template('admin_login.html')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
            return

        # Protected routes
        if self.path.startswith('/admin/'):
            if not self.require_auth():
                return
                
            if self.path == '/admin/dashboard':
                self.serve_dashboard()
                return
            elif self.path == '/admin/certificates':
                self.serve_certificates()
                return
            elif self.path == '/admin/certificates/new':
                self.serve_certificate_form()
                return
            elif self.path.startswith('/admin/certificates/edit/'):
                cert_number = self.path.split('/admin/certificates/edit/')[1]
                self.serve_certificate_form(cert_number)
                return
            elif self.path == '/admin/settings':
                self.serve_settings()
                return

        # Serve static files
        if self.path.startswith('/static/'):
            file_path = self.path[1:]
            if file_path.endswith('.css'):
                self.serve_file(file_path, 'text/css')
            elif file_path.endswith('.js'):
                self.serve_file(file_path, 'text/javascript')
            return

        # Serve main page
        if self.path == '/':
            content = self.load_template('index.html')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
            return

        # Handle direct certificate verification (QR code or form redirect)
        if self.path.startswith('/verify/'):
            parsed_path = urllib.parse.urlparse(self.path)
            cert_number = parsed_path.path.split('/verify/')[1]
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # Get name parameters if they exist
            last_name = query_params.get('lastName', [''])[0]
            first_name = query_params.get('firstName', [''])[0]
            
            # Verify certificate with names if provided
            result = self.verify_certificate(cert_number, last_name, first_name)
            
            html = self.generate_verification_html(
                result.get('data', {'message': result.get('message')}),
                result['status']
            )
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # Handle API requests
        if self.path.startswith('/api/verify/'):
            parsed_path = urllib.parse.urlparse(self.path)
            cert_number = parsed_path.path.split('/api/verify/')[1]
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            last_name = query_params.get('lastName', [''])[0]
            first_name = query_params.get('firstName', [''])[0]
            
            result = self.verify_certificate(cert_number, last_name, first_name)
            
            # Check if the client accepts JSON
            accepts = self.headers.get('Accept', '')
            if 'application/json' in accepts:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            else:
                html = self.generate_verification_html(
                    result.get('data', {'message': result.get('message')}),
                    result['status']
                )
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            return

        # Add this at the start of do_GET
        if self.path == '/admin/logout':
            cookie = SimpleCookie(self.headers.get('Cookie'))
            session_id = cookie.get('session_id')
            
            if session_id:
                expired_cookie = self.remove_session(session_id.value)
                self.send_response(302)
                self.send_header('Location', '/admin/login')
                self.send_header('Set-Cookie', expired_cookie['session_id'].OutputString())
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/admin/login')
                self.end_headers()
            return

        # Certificate management routes
        if self.path == '/admin/certificates/new':
            self.serve_certificate_form()
            return
        elif self.path.startswith('/admin/certificates/edit/'):
            cert_number = self.path.split('/')[-1]
            self.serve_certificate_form(cert_number)
            return
        elif self.path == '/admin/certificates':
            self.serve_certificates_list()
            return

        # Admin management routes - require admin role
        if self.path.startswith('/admin/admins'):
            if not self.require_auth():
                return
            if not self.check_admin_permission():
                return
            
            if self.path == '/admin/admins/new':
                self.serve_admin_form()
                return
            elif self.path.startswith('/admin/admins/edit/'):
                admin_id = self.path.split('/')[-1]
                self.serve_admin_form(admin_id)
                return
            elif self.path == '/admin/admins':
                self.serve_admins_list()
                return

    def do_POST(self):
        if self.path == '/admin/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            try:
                with open('data/admin.json', 'r') as f:
                    admins = json.load(f)
                
                for admin in admins['administrators']:
                    if admin['username'] == username:
                        if check_password_hash(admin['password_hash'], password):
                            # Create session
                            cookie = self.create_session(admin)
                            
                            self.send_response(302)
                            self.send_header('Set-Cookie', cookie['session_id'].OutputString())
                            self.send_header('Location', '/admin/dashboard')
                            self.end_headers()
                            return
                
                # Invalid credentials
                self.send_response(302)
                self.send_header('Location', '/admin/login?error=1')
                self.end_headers()
                
            except Exception as e:
                print(f"Login error: {e}")
                self.send_response(500)
                self.end_headers()

        elif self.path == '/admin/admins/new':
            if not self.require_auth() or not self.check_admin_permission():
                return
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            
            try:
                # Load existing admins
                with open('data/admin.json', 'r') as f:
                    admins = json.load(f)
                
                # Get form data
                username = form_data.get('username', [''])[0]
                password = form_data.get('password', [''])[0]
                role = form_data.get('role', ['user'])[0]
                
                # Validate required fields
                if not username or not password:
                    self.send_error(400, 'Username and password are required')
                    return
                
                # Check if username already exists
                if any(admin['username'] == username for admin in admins['administrators']):
                    self.send_error(400, 'Username already exists')
                    return
                
                # Ensure only admins can create admin accounts
                session = self.get_session()
                if role == 'admin' and session['role'] != 'admin':
                    self.send_error(403, 'Insufficient permissions to create admin accounts')
                    return
                
                # Create password hash
                from werkzeug.security import generate_password_hash
                password_hash = generate_password_hash(password, method='scrypt')
                
                # Create new admin
                new_admin = {
                    'username': username,
                    'password_hash': password_hash,
                    'role': role
                }
                
                # Add new admin
                admins['administrators'].append(new_admin)
                
                # Save updated admins
                with open('data/admin.json', 'w') as f:
                    json.dump(admins, f, indent=4)
                
                # Redirect to admins list
                self.send_response(302)
                self.send_header('Location', '/admin/admins')
                self.end_headers()
                
            except Exception as e:
                print(f"Error creating admin: {e}")
                self.send_error(500, str(e))
                
        elif self.path == '/admin/certificates/new':
            if not self.require_auth():
                return
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            
            try:
                # Get the current date for the certificate number
                issue_date = datetime.now()
                
                # Load existing certificates to get the next number
                with open('data/certificates.json', 'r') as f:
                    certs = json.load(f)
                
                # Calculate the next certificate number
                current_year = datetime.now().year
                year_certs = [c for c in certs['certificates'] 
                             if c['cert_type']['year'] == current_year]
                next_number = len(year_certs) + 1
                
                # Generate the certificate number
                cert_number = self.generate_cert_number(
                    current_year,
                    next_number,
                    issue_date
                )
                
                # Handle phone number (can be null)
                phone = form_data.get('contact[phone]', [''])[0]
                if not phone or phone.strip() == '':
                    phone = "null"
                
                # Create new certificate
                new_cert = {
                    'cert_number': cert_number,  # Automatically generated
                    'cert_type': {
                        'type': form_data.get('cert_type[type]', [''])[0],
                        'year': current_year,  # Use current year
                        'number': next_number,  # Automatically calculated
                        'title': form_data.get('cert_type[title]', [''])[0],
                        'description': form_data.get('cert_type[description]', [''])[0]
                    },
                    'owner': form_data.get('owner', [''])[0],
                    'birthdate': form_data.get('birthdate', [''])[0],
                    'address': {
                        'street': form_data.get('address[street]', [''])[0],
                        'no': form_data.get('address[no]', [''])[0],
                        'city': form_data.get('address[city]', [''])[0],
                        'zip': form_data.get('address[zip]', [''])[0]
                    },
                    'contact': {
                        'phone': phone,  # Can be "null"
                        'email': form_data.get('contact[email]', [''])[0]
                    },
                    'expire_date': form_data.get('expire_date', [''])[0],
                    'is_valid': True
                }
                
                # Add new certificate
                certs['certificates'].append(new_cert)
                
                # Save updated certificates
                with open('data/certificates.json', 'w') as f:
                    json.dump(certs, f, indent=4)
                
                # Redirect to certificates list
                self.send_response(302)
                self.send_header('Location', '/admin/certificates')
                self.end_headers()
                
            except Exception as e:
                print(f"Error creating certificate: {e}")
                self.send_response(500)
                self.end_headers()

    def do_PUT(self):
        if not self.require_auth():
            return

        # Handle certificate updates
        if self.path.startswith('/admin/certificates/edit/'):
            cert_number = self.path.split('/admin/certificates/edit/')[1]
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(put_data)
            
            try:
                with open('data/certificates.json', 'r') as f:
                    certs = json.load(f)
                
                # Find the certificate to update
                cert_index = next((i for i, cert in enumerate(certs['certificates']) 
                             if cert['cert_number'] == cert_number), None)
                
                if cert_index is not None:
                    # Preserve existing cert_type fields
                    existing_cert = certs['certificates'][cert_index]
                    
                    # Update certificate data
                    updated_cert = {
                        'cert_number': cert_number,  # Keep original number
                        'cert_type': {
                            'type': form_data.get('cert_type[type]', [''])[0],
                            'year': existing_cert['cert_type']['year'],  # Preserve year
                            'number': existing_cert['cert_type']['number'],  # Preserve number
                            'title': form_data.get('cert_type[title]', [''])[0],
                            'description': form_data.get('cert_type[description]', [''])[0]
                        },
                        'owner': form_data.get('owner', [''])[0],
                        'birthdate': form_data.get('birthdate', [''])[0],
                        'address': {
                            'street': form_data.get('address[street]', [''])[0],
                            'no': form_data.get('address[no]', [''])[0],
                            'city': form_data.get('address[city]', [''])[0],
                            'zip': form_data.get('address[zip]', [''])[0]
                        },
                        'contact': {
                            'phone': form_data.get('contact[phone]', [''])[0] or None,
                            'email': form_data.get('contact[email]', [''])[0]
                        },
                        'expire_date': form_data.get('expire_date', [''])[0],
                        'is_valid': existing_cert['is_valid']  # Preserve validity status
                    }
                    
                    # Update the certificate
                    certs['certificates'][cert_index] = updated_cert
                    
                    # Save updated certificates
                    with open('data/certificates.json', 'w') as f:
                        json.dump(certs, f, indent=4)
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                else:
                    self.send_error(404, 'Certificate not found')
                    
            except Exception as e:
                print(f"Error updating certificate: {e}")
                self.send_error(500, str(e))

        # Handle admin updates
        elif self.path.startswith('/admin/admins/edit/'):
            admin_id = self.path.split('/admin/admins/edit/')[1]
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(put_data)
            
            try:
                with open('data/admin.json', 'r') as f:
                    admins = json.load(f)
                
                # Find the admin to update
                admin_index = next((i for i, admin in enumerate(admins['administrators']) 
                                  if admin['username'] == admin_id), None)
                
                if admin_index is not None:
                    # Update admin data
                    admin = admins['administrators'][admin_index]
                    
                    # Update password only if provided
                    if form_data.get('password', [''])[0]:
                        from werkzeug.security import generate_password_hash
                        admin['password_hash'] = generate_password_hash(
                            form_data['password'][0], 
                            method='scrypt'
                        )
                    
                    # Update role
                    admin['role'] = form_data.get('role', ['admin'])[0]
                    
                    # Save updated admins
                    with open('data/admin.json', 'w') as f:
                        json.dump(admins, f, indent=4)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                else:
                    self.send_error(404, 'Admin not found')
                    
            except Exception as e:
                print(f"Error updating admin: {e}")
                self.send_error(500, str(e))

    def do_DELETE(self):
        if not self.require_auth():
            return
        
        session = self.get_session()
        if session['role'] != 'admin':
            self.send_error(403, 'Only administrators can delete certificates')
            return
        
        # Handle certificate deletion
        if self.path.startswith('/admin/certificates/delete/'):
            cert_number = self.path.split('/admin/certificates/delete/')[1]
            
            try:
                # Load existing certificates
                with open('data/certificates.json', 'r') as f:
                    certs = json.load(f)
                
                # Find and remove the certificate
                initial_length = len(certs['certificates'])
                certs['certificates'] = [c for c in certs['certificates'] 
                                       if c['cert_number'] != cert_number]
                
                # Check if certificate was actually removed
                if len(certs['certificates']) == initial_length:
                    self.send_error(404, 'Certificate not found')
                    return
                
                # Save updated certificates
                with open('data/certificates.json', 'w') as f:
                    json.dump(certs, f, indent=4)
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
                
            except Exception as e:
                print(f"Error deleting certificate: {e}")
                self.send_error(500, str(e))
            
        # Handle admin deletion
        elif self.path.startswith('/admin/admins/delete/'):
            username = self.path.split('/admin/admins/delete/')[1]
            
            try:
                # Don't allow deletion of the main admin account
                if username == 'admin':
                    self.send_error(403, 'Cannot delete main administrator account')
                    return
                
                # Load existing admins
                with open('data/admin.json', 'r') as f:
                    admins = json.load(f)
                
                # Find and remove the admin
                initial_length = len(admins['administrators'])
                admins['administrators'] = [a for a in admins['administrators'] 
                                         if a['username'] != username]
                
                # Check if admin was actually removed
                if len(admins['administrators']) == initial_length:
                    self.send_error(404, 'Administrator not found')
                    return
                
                # Save updated admins
                with open('data/admin.json', 'w') as f:
                    json.dump(admins, f, indent=4)
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
                
            except Exception as e:
                print(f"Error deleting administrator: {e}")
                self.send_error(500, str(e))

    def serve_dashboard(self):
        try:
            with open('data/certificates.json', 'r') as f:
                certs = json.load(f)
            
            now = datetime.now()
            thirty_days = timedelta(days=30)
            
            # Calculate statistics
            total_certs = len(certs['certificates'])
            valid_certs = 0
            expiring_soon = 0
            expired_certs = 0
            cert_types = set()
            
            for cert in certs['certificates']:
                expire_date = datetime.strptime(cert['expire_date'], '%Y-%m-%d')
                cert_types.add(cert.get('type', 'Unknown'))
                
                if expire_date > now:
                    valid_certs += 1
                    if expire_date - now <= thirty_days:
                        expiring_soon += 1
                else:
                    expired_certs += 1
            
            content = self.load_template('admin_dashboard.html')
            session = self.get_session()
            
            # Prepare admin button HTML
            admin_button = '''
                <button class="action-btn" onclick="location.href='/admin/admins/new'">
                    <i class="material-icons">person_add</i>
                    New Admin
                </button>
            ''' if session and session['role'] == 'admin' else ''
            
            replacements = {
                '{{total_certs}}': str(total_certs),
                '{{valid_certs}}': str(valid_certs),
                '{{expiring_soon}}': str(expiring_soon),
                '{{expired_certs}}': str(expired_certs),
                '{{cert_types}}': str(len(cert_types)),
                '{{ADMIN_BUTTON}}': admin_button
            }
            
            for key, value in replacements.items():
                content = content.replace(key, value)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
            
        except Exception as e:
            print(f"Dashboard error: {e}")
            self.send_error(500)

    def serve_certificates_list(self):
        try:
            with open('data/certificates.json', 'r') as f:
                certs = json.load(f)
        
            session = self.get_session()
            content = self.load_template('certificates_list.html')
            
            # Add admin menu item if user is admin
            admin_menu_item = '''
                <li>
                    <a href="/admin/admins" style="text-decoration: none; color: inherit;">
                        <i class="material-icons">group</i>
                        <span>Admins</span>
                    </a>
                </li>
            ''' if session['role'] == 'admin' else ''
            
            # Convert certificates data to JSON string and embed it safely
            certificates_json = json.dumps(certs['certificates'])
            content = content.replace('{{CERTIFICATES_DATA}}', certificates_json)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            print(f"Error loading certificates: {e}")
            self.send_error(500)

    def serve_certificate_form(self, cert_number=None):
        try:
            content = self.load_template('certificate_form.html')
            if cert_number:
                with open('data/certificates.json', 'r') as f:
                    certs = json.load(f)
                    cert_data = next((c for c in certs['certificates'] 
                                    if c['cert_number'] == cert_number), None)
                    if cert_data:
                        content = content.replace('{{{CERTIFICATE_DATA}}}', 
                                               json.dumps(cert_data))
            else:
                content = content.replace('{{{CERTIFICATE_DATA}}}', '{}')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            print(f"Error serving certificate form: {e}")
            self.send_error(500)

    def serve_admin_form(self, admin_id=None):
        try:
            content = self.load_template('admin_form.html')
            if admin_id:
                with open('data/admin.json', 'r') as f:
                    admins = json.load(f)
                    admin_data = next((a for a in admins['administrators'] 
                                     if a['username'] == admin_id), None)
                    if admin_data:
                        # Remove sensitive data
                        admin_data.pop('password_hash', None)
                        content = content.replace('{{{ADMIN_DATA}}}', 
                                               json.dumps(admin_data))
            else:
                content = content.replace('{{{ADMIN_DATA}}}', '{}')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            print(f"Error serving admin form: {e}")
            self.send_error(500)

    def serve_certificates(self):
        try:
            with open('data/certificates.json', 'r') as f:
                certs = json.load(f)
            
            content = self.load_template('certificates_list.html')
            # Convert certificates data to JSON string and embed it safely
            certificates_json = json.dumps(certs['certificates']).replace("'", "\\'")
            content = content.replace('{{CERTIFICATES_DATA}}', certificates_json)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            print(f"Error loading certificates: {e}")
            self.send_error(500)

    def serve_admins_list(self):
        try:
            with open('data/admin.json', 'r') as f:
                admins = json.load(f)
            
            content = self.load_template('admins_list.html')
            # Remove sensitive data before sending to client
            safe_admins = []
            for admin in admins['administrators']:
                safe_admin = admin.copy()
                safe_admin.pop('password_hash', None)
                safe_admins.append(safe_admin)
                
            admins_json = json.dumps(safe_admins)
            content = content.replace('{{ADMINS_DATA}}', admins_json)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            print(f"Error loading admins: {e}")
            self.send_error(500)

    def show_error_page(self, message):
        """Show error page with toast notification"""
        content = self.load_template('error.html')
        content = content.replace('{{ERROR_MESSAGE}}', message)
        self.send_response(403)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode())

def run_server(port=5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CertHandler)
    print(f'Starting server on port {port}...')
    print(f'Visit http://localhost:{port} to verify certificates')
    print(f'For QR codes use: http://localhost:{port}/verify/<cert_number>')
    print(f'For API calls use: curl -H "Accept: application/json" http://localhost:{port}/api/verify/<cert_number>')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
