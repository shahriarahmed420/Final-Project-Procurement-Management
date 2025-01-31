from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, fields
from odoo.http import request
from datetime import date
import base64

class OTPCustomerPortal(CustomerPortal):
    @http.route(['/my/supplier'], type='http', auth='public', website=True)
    def my_supplier_page(self):
        return request.render('procurement_management.supplier_page_template', {
            'page_name': 'my_supplier',
        })

    @http.route(['/my/supplier/check'], type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def my_supplier_check(self, **kwargs):
        email = kwargs.get('email')

        if not email:
            return request.render('procurement_management.supplier_mail_template', {
                'page_name': 'my_supplier',
                'error': 'Email is required, Must!'
            })

        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return request.render('procurement_management.supplier_mail_template', {
                'page_name': 'my_supplier',
                'error': 'An account with this email is already exists!'
            })

        existing_partner = request.env['res.partner'].sudo().search([('email', '=', email), ('supplier_rank', '>', 0)], limit=1)
        if existing_partner:
            return request.render('procurement_management.supplier_mail_template', {
                'page_name': 'my_supplier',
                'error': 'A supplier with this email is already exists!'
            })

        blacklisted = request.env['supplier.blacklist'].sudo().search([('email', '=', email)], limit=1)
        if blacklisted:
            return request.render('procurement_management.supplier_mail_template', {
                'page_name': 'my_supplier',
                'error': 'This email is blacklisted, you can not go further!'
            })

        return request.render('procurement_management.otp_verification_template', {
            'page_name': 'my_otp',
        })

    @http.route(['/my/otp'], type='http', auth='public', website=True)
    def my_otp_verification(self):
        return request.render('procurement_management.otp_verification_template', {
            'page_name': 'my_otp',
        })

    @http.route(['/my/otp/send'], type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def send_otp(self, **kwargs):
        email = kwargs.get('email')
        if not email:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Email is required',
            })

        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Email is already registered',
            })

        otp_record = request.env['supplier.otp'].sudo().generate_otp(email)
        if not otp_record:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Failed to generate OTP',
            })

        # Optionally send the OTP via email
        request.env['mail.mail'].sudo().create({
            'email_from': 'shahriar.ahmed@bjitacademy.com',
            'email_to': email,
            'subject': 'Your OTP Code',
            'body_html': f'<p>Your OTP code is: <strong>{otp_record.otp}</strong>. It is valid for 5 minutes.</p>'
        }).send()

        # Render the OTP input form
        return request.render('procurement_management.otp_verification_template', {
            'email': email,
            'show_otp_section': True,
        })

    @http.route(['/my/otp/verify'], type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def verify_otp(self, **kwargs):
        email = kwargs.get('email')
        otp = kwargs.get('otp')

        if not email or not otp:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Email and OTP are required!',
                'show_otp_section': True
            })

        otp_valid = request.env['supplier.otp'].sudo().validate_otp(email, otp)

        if otp_valid:
            request.session['supplier_email'] = email
            return request.redirect('/my/supplier/form')
        else:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Invalid OTP. Please try again.',
                'show_otp_section': True
            })

    @http.route(['/my/supplier/form'], type='http', auth='public', website=True, csrf=True)
    def supplier_form(self, **kwargs):
        if not request.session.get('supplier_email'):
            request.session['supplier_email'] = kwargs.get('email')  # Restore from URL

        supplier_email = request.session.get('supplier_email')

        if not supplier_email:
            return request.redirect('/my/home')

        return request.render('procurement_management.supplier_registration_form_template', {
            'supplier_email': supplier_email,
            'current_date': fields.Date.today(),
        })

    @http.route(['/my/supplier/form/submit'], type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def submit_supplier_form(self, **kwargs):
        """ Handles the final supplier form submission when the user reaches the last step. """
        supplier_email = request.session.get('supplier_email')

        print("🔍 Checking session: supplier_email =", supplier_email)

        if not supplier_email:
            print("❌ ERROR: Supplier email not found in session. Redirecting to home.")
            return request.redirect('/my/home')

        # ✅ Required Fields Validation
        required_fields = [
            "company_name", "company_address", "company_type",
            "primary_contact_name", "primary_contact_email", "primary_contact_phone",
            "finance_contact_name", "finance_contact_email", "finance_contact_phone",
            "authorized_contact_name", "authorized_contact_email", "authorized_contact_phone",
            "bank_name", "bank_address", "account_number",
            "client_name", "certification_name", "certificate_number"
        ]

        missing_fields = [field for field in required_fields if not kwargs.get(field)]
        if missing_fields:
            print("⚠️ MISSING FIELDS:", missing_fields)
            return request.render('procurement_management.supplier_registration_form_template', {
                'error': f"⚠️ Please fill in all required fields: {', '.join(missing_fields)}",
                'supplier_email': supplier_email,
                'form_data': kwargs
            })

        # ✅ Retrieve or Create Registration Record
        registration = request.env['registration.form'].sudo().search([('email', '=', supplier_email)], limit=1)

        if not registration:
            try:
                registration = request.env['registration.form'].sudo().create({
                    'email': supplier_email,
                    **{key: kwargs.get(key) for key in required_fields}
                })
                print("✅ Supplier Registration Created Successfully:", registration.id)
            except Exception as e:
                print(f"❌ ERROR Creating Registration: {e}")
                return request.render('procurement_management.supplier_registration_form_template', {
                    'error': f"❌ Failed to create registration: {str(e)}",
                    'supplier_email': supplier_email,
                    'form_data': kwargs
                })

        # ✅ Handle File Uploads (Convert FileStorage to Proper Base64 Binary)
        file_fields = [
            'documents'  # Add all binary fields here
        ]
        file_vals = {}

        for field in file_fields:
            file_obj = kwargs.get(field)

            if file_obj and hasattr(file_obj, 'read'):  # Ensure it's a file object
                try:
                    file_content = file_obj.read()  # Read binary content
                    encoded_file = base64.b64encode(file_content)  # Encode to base64 (bytes)
                    file_vals[field] = encoded_file
                    print(f"✅ File '{field}' processed successfully and converted to binary.")
                except Exception as e:
                    print(f"❌ ERROR Processing File '{field}': {e}")

        # ✅ Save Final Form Data
        try:
            registration.sudo().write(kwargs)
            if file_vals:
                registration.sudo().write(file_vals)  # Save uploaded files
            print("✅ Supplier Registration Updated Successfully:", registration.id)
        except Exception as e:
            print(f"❌ ERROR Updating Registration: {e}")
            return request.render('procurement_management.supplier_registration_form_template', {
                'error': f"❌ Failed to update registration data: {str(e)}",
                'supplier_email': supplier_email,
                'form_data': kwargs
            })

        # ✅ Remove Session & Redirect to Success Page
        request.session.pop('supplier_email', None)

        print("🎉 SUCCESS: Redirecting to success page.")
        return request.redirect('/my/supplier/form/success')

    @http.route(['/my/supplier/form/success'], type='http', auth='public', website=True, csrf=False)
    def supplier_form_success(self):
        """ Displays the success message after form submission. """
        return request.render('procurement_management.supplier_registration_success_template')
