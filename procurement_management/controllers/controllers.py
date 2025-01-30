from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request

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
    def my_otp_verification(self, **kw):
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
                'error': 'Email and OTP are required',
                'show_otp_section': True,
                'email': email,
            })

        valid = request.env['supplier.otp'].sudo().validate_otp(email, otp)
        if valid:
            return request.redirect('/my/supplier/form?email=%s' % email)
        else:
            return request.render('procurement_management.otp_verification_template', {
                'error': 'Invalid OTP. Please try again.',
                'show_otp_section': True,
                'email': email,
            })

    @http.route(['/my/supplier/form'], type='http', auth='public', website=True, csrf=True)
    def supplier_form(self, **kwargs):
        email = kwargs.get('email')
        if not email:
            return request.render('procurement_management.supplier_registration_form_template', {
                'error': 'Email is required to proceed to the form.',
            })
        return request.render('procurement_management.supplier_registration_form_template', {
            'email': email,
        })

    @http.route(['/my/supplier/form/submit'], type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def submit_supplier_form(self, **kwargs):
        # Extract form data
        company_name = kwargs.get('company_name')
        company_address = kwargs.get('company_address')
        company_type = kwargs.get('company_type')

        # Save data to the model
        request.env['registration.form'].sudo().create({
            'company_name': company_name,
            'company_address': company_address,
            'company_type': company_type,
        })

        return request.redirect('/my/home')