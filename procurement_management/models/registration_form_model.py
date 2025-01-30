from odoo import models, fields, api


class RegistrationFormContact(models.Model):
    _name = 'registration.form.contact'
    _description = "Registration Form Contact"

    name = fields.Char("Name", required=True)
    email = fields.Char("Email", required=True)
    phone = fields.Char("Phone", required=True)
    address = fields.Text("Address")


class RegistrationFormClientReference(models.Model):
    _name = 'registration.form.client.reference'
    _description = "Registration Form Client Reference"

    form_id = fields.Many2one('registration.form', string="Registration Form", ondelete='cascade')
    name = fields.Char("Client Name", required=True)
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    address = fields.Text("Address")


class RegistrationFormCertification(models.Model):
    _name = 'registration.form.certification'
    _description = "Registration Form Certification"

    form_id = fields.Many2one('registration.form', string="Registration Form", ondelete='cascade')
    name = fields.Char("Certification Name", required=True)
    certificate_number = fields.Char("Certificate Number", required=True)
    certifying_body = fields.Char("Certifying Body")
    award_date = fields.Date("Award Date")
    expiry_date = fields.Date("Expiry Date")


# class RegistrationFormDocument(models.Model):
#     _name = 'registration.form.document'
#     _description = "Registration Form Document"
#
#     form_id = fields.Many2one('registration.form', string="Registration Form", ondelete='cascade')
#     document_name = fields.Char("Document Name")
#     attachment = fields.Binary("Attachment")


class RegistrationForm(models.Model):
    _name = 'registration.form'
    _description = 'A model to view and track for supplier form'

    # Section-1

    company_name = fields.Char("Company Name", required=True)
    company_address = fields.Char("Company Address", required=True)
    company_type = fields.Selection([
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('llc', 'Limited Liability Company (LLC)'),
        ('corporation', 'Corporation'),
        ('s_corporation', 'S Corporation'),
        ('cooperative', 'Cooperative'),
        ('non_profit', 'Non-Profit Organization'),
        ('government_agency', 'Government Agency'),
        ('joint_venture', 'Joint Venture'),
        ('holding_company', 'Holding Company'),
        ('private_limited', 'Private Limited Company'),
        ('public_limited', 'Public Limited Company'),
    ], string="Company Type", required=True)
    company_logo = fields.Binary("Company logo")
    primary_contact_id = fields.Many2one('registration.form.contact', string='Primary Contact', required=True)
    finance_contact_id = fields.Many2one('registration.form.contact', string='Finance Contact')
    authorized_contact_id = fields.Many2one('registration.form.contact', string='Authorized Contact')
    trade_license_no = fields.Char("Trade License Number", help="Range - 8-20 characters")
    commencement_date = fields.Date("Commencement Date")
    expiry_date = fields.Date("Expiry Date")
    tax_id_num = fields.Char("Tax Identification Number (TIN)", size=16)

    # Section - 2

    bank_name = fields.Char("Bank Name", required=True)
    bank_address = fields.Text("Bank Address", required=True)
    bank_swift_code = fields.Char("SWIFT Code")
    account_name = fields.Char("Account Name")
    account_number = fields.Char("Account Number", required=True)
    iban = fields.Char("IBAN")

    # Section - 3

    client_reference_ids = fields.One2many('registration.form.client.reference', 'form_id', string="Client References")

    # Section - 4

    certification_ids = fields.One2many('registration.form.certification', 'form_id', string="Certifications")

    # Section - 5

    # document_ids = fields.One2many('registration.form.document', 'form_id', string="Uploaded Documents")

    # Status Tracking

    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('submitted', 'Submitted'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected'),
    # ], string="Status", default='draft')