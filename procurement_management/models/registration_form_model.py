from odoo import models, fields, api


class RegistrationForm(models.Model):
    _name = 'registration.form'
    _description = 'A model to view and track for supplier form'

    email = fields.Char("Supplier Email", required=True, index=True)

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

    primary_contact_name = fields.Char("Name", required=True)
    primary_contact_email = fields.Char("Email", required=True)
    primary_contact_phone = fields.Char("Phone", required=True)
    primary_contact_address = fields.Text("Address")

    finance_contact_name = fields.Char("Name", required=True)
    finance_contact_email = fields.Char("Email", required=True)
    finance_contact_phone = fields.Char("Phone", required=True)
    finance_contact_address = fields.Text("Address")

    authorized_contact_name = fields.Char("Name", required=True)
    authorized_contact_email = fields.Char("Name", required=True)
    authorized_contact_phone = fields.Char("Name", required=True)
    authorized_contact_address = fields.Char("Name")

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

    client_name = fields.Char("Client Name", required=True)
    client_email = fields.Char("Email")
    client_phone = fields.Char("Phone")
    client_address = fields.Text("Address")

    # Section - 4

    certification_name = fields.Char("Certification Name", required=True)
    certificate_number = fields.Char("Certificate Number", required=True)
    certifying_body = fields.Char("Certifying Body")
    award_date = fields.Date("Award Date")
    certificate_expiry_date = fields.Date("Expiry Date")

    documents = fields.Binary()