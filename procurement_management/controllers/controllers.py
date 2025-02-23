from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, fields
from odoo.http import request
import werkzeug.datastructures
from datetime import date
import base64
from odoo.exceptions import ValidationError


def process_uploaded_file(file_obj, chunk_size=8192):
    if file_obj and hasattr(file_obj, 'read'):
        try:
            file_obj.seek(0)
            file_content = b""
            while chunk := file_obj.read(chunk_size):
                file_content += chunk
            return base64.b64encode(file_content)
        except Exception as e:
            print(f"🚨 ERROR Processing File: {e}")
    return False


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

        # ✅ Check if an Odoo User exists with this email
        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return request.render('procurement_management.supplier_mail_template', {
                'page_name': 'my_supplier',
                'error': 'An account with this email already exists!'
            })

        # ✅ Check if a Supplier exists (Alternative to `supplier_rank`)
        existing_supplier = request.env['res.partner'].sudo().search([
            ('email', '=', email),
            ('is_company', '=', True),  # ✅ Ensure it's a company
        ], limit=1)

        if existing_supplier:
            return request.render('procurement_management.supplier_mail_template', {
                'page_name': 'my_supplier',
                'error': 'A supplier with this email already exists!'
            })

        # ✅ Check if the email is blacklisted
        blacklisted = request.env['supplier.blacklist'].sudo().search([('email', '=', email)], limit=1)
        if blacklisted:
            return request.render('procurement_management.supplier_mail_template', {
                'page_name': 'my_supplier',
                'error': 'This email is blacklisted, you cannot go further!'
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

        # ✅ DEBUG: Check if OTP is being generated
        otp_record = request.env['supplier.otp'].sudo().generate_otp(email)
        if not otp_record:
            print("❌ OTP Generation Failed for:", email)
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Failed to generate OTP',
            })

        print(f"✅ OTP Generated: {otp_record.otp} for {email}")

        # ✅ Send OTP Email
        email_values = {
            'email_from': 'shahriar.ahmed@bjitacademy.com',
            'email_to': email,
            'subject': 'Your OTP Code',
            'body_html': f'<p>Your OTP code is: <strong>{otp_record.otp}</strong>. It is valid for 5 minutes.</p>'
        }

        try:
            mail = request.env['mail.mail'].sudo().create(email_values)
            print(f"✅ Email Created: ID {mail.id} for {email}")
            mail.sudo().send()
            print(f"✅ Email Sent to {email}")
        except Exception as e:
            print(f"❌ Email Sending Failed: {e}")
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Failed to send OTP email. Please try again.',
            })

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
        supplier_email = request.session.get('supplier_email')

        print("Checking session: supplier_email =", supplier_email)

        if not supplier_email:
            print("ERROR: Supplier email not found in session. Redirecting to home.")
            return request.redirect('/my/home')

        # ✅ Define required fields
        required_fields = [
            "company_name", "company_address", "company_type", "primary_contact_name", "primary_contact_email", "primary_contact_phone",
            "finance_contact_name", "finance_contact_email", "finance_contact_phone", "authorized_contact_name", "authorized_contact_email",
            "authorized_contact_phone", "bank_name", "bank_address", "account_number", "certification_name", "certificate_number",
            "name_of_signatory", "authorized_signatory"
        ]

        missing_fields = [field for field in required_fields if not kwargs.get(field)]
        if missing_fields:
            print("MISSING FIELDS:", missing_fields)
            return request.render('procurement_management.supplier_registration_form_template', {
                'error': f"Please fill in all required fields: {', '.join(missing_fields)}",
                'supplier_email': supplier_email,
                'form_data': kwargs
            })

        registration = request.env['registration.form'].sudo().search([('email', '=', supplier_email)], limit=1)

        if not registration:
            try:
                registration = request.env['registration.form'].sudo().create({
                    'email': supplier_email,
                    **{key: kwargs.get(key) for key in required_fields}
                })
                print("Supplier Registration Created Successfully:", registration.id)
            except Exception as e:
                print(f"❌ ERROR Creating Registration: {e}")
                return request.render('procurement_management.supplier_registration_form_template', {
                    'error': f"❌ Failed to create registration: {str(e)}",
                    'supplier_email': supplier_email,
                    'form_data': kwargs
                })

        # ✅ Process Uploaded Files and Convert to Binary in Chunks
        file_fields = [
            'trade_license_business_registration', 'certificate_of_incorporation',
            'certificate_of_good_standing',
            'establishment_card', 'vat_tax_certificate', 'memorandum_of_association',
            'identification_document_for_authorized_person', 'bank_letter_indicating_bank_account',
            'past_2_years_audited_financial_statements', 'other_certifications', 'company_stamp'
        ]

        file_vals = {}

        for field in file_fields:
            file_obj = kwargs.get(field)
            if isinstance(file_obj, werkzeug.datastructures.FileStorage):
                encoded_file = process_uploaded_file(file_obj)
                if encoded_file:
                    file_vals[field] = encoded_file
                    print(f"✅ File '{field}' processed successfully.")

        try:
            registration.sudo().write(
                {key: kwargs[key] for key in kwargs if key not in file_fields})  # ✅ Save normal fields
            if file_vals:
                registration.sudo().write(file_vals)  # ✅ Save file fields
            print("✅ Supplier Registration Updated Successfully:", registration.id)

            reviewer_group = request.env.ref('procurement_management.group_supplier_reviewer')
            approver_group = request.env.ref('procurement_management.group_supplier_approver')
            reviewers = request.env['res.users'].sudo().search([
                ('groups_id', 'in', reviewer_group.id),
                ('groups_id', 'not in', approver_group.id),
                ('email', '!=', False),
                ('email', '!=', 'admin@yourcompany.example.com')
            ])

            for reviewer in reviewers:
                email_values = {
                    'email_from': 'shahriar.ahmed@bjitacademy.com',
                    'email_to': reviewer.email,
                    'subject': 'New Supplier Registration Request',
                    'body_html': '<p>A new supplier registration request has been submitted. Please review it.</p>'
                }
                mail = request.env['mail.mail'].sudo().create(email_values)
                print(f"✅ Email Created: ID {mail.id} for {reviewer.email}")
                mail.sudo().send()
                print(f"✅ Email Sent to {reviewer.email}")

        except Exception as e:
            print(f"ERROR Updating Registration: {e}")
            return request.render('procurement_management.supplier_registration_form_template', {
                'error': f"❌ Failed to update registration data: {str(e)}",
                'supplier_email': supplier_email,
                'form_data': kwargs
            })


        request.session.pop('supplier_email', None)

        print("SUCCESS: Redirecting to success page.")
        return request.redirect('/my/supplier/form/success')


    @http.route(['/my/supplier/form/success'], type='http', auth='public', website=True, csrf=False)
    def supplier_form_success(self):

        return request.render('procurement_management.supplier_registration_success_template')