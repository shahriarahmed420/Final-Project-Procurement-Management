from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
    authorized_contact_email = fields.Char("Email", required=True)
    authorized_contact_phone = fields.Char("Phone", required=True)
    authorized_contact_address = fields.Char("Address")

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

    # Section - 5

    trade_license_business_registration = fields.Binary(string='Trade License/Business Registration')
    certificate_of_incorporation = fields.Binary(string='Certificate of Incorporation')
    certificate_of_good_standing = fields.Binary(string='Certificate of Good Standing')
    establishment_card = fields.Binary(string='Establishment Card')
    vat_tax_certificate = fields.Binary(string='VAT/TAX Certificate')
    memorandum_of_association = fields.Binary(string='Memorandum of Association')
    identification_document_for_authorized_person = fields.Binary(string='Identification Document for Authorized Person')
    bank_letter_indicating_bank_account = fields.Binary(string='Bank Letter indicating Bank Account')
    past_2_years_audited_financial_statements = fields.Binary(string='Past 2 Years Audited Financial Statements')
    other_certifications = fields.Binary(string='Other Certifications')

    name_of_signatory = fields.Char(string="Name of Signatory", required=True)
    authorized_signatory = fields.Char(string="Authorized Signatory Role", required=True)
    company_stamp = fields.Binary(string="Company Stamp", required=True)
    submission_date = fields.Date(string="Submission Date", required=True, default=fields.Date.context_today)\

    state = fields.Selection(
        [('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        string='State', default='submitted')

    @api.constrains('certificate_expiry_date')
    def _check_certificate_expiry(self):
        for record in self:
            if record.certificate_expiry_date and record.certificate_expiry_date <= fields.Date.today():
                raise ValidationError("Certificate expiry date must be in the future.")

    @api.constrains('trade_license_business_registration', 'certificate_of_incorporation')
    def _check_file_size(self):
        for record in self:
            max_size = 5 * 1024 * 1024  # 5 MB
            if record.trade_license_business_registration and len(
                    record.trade_license_business_registration) > max_size:
                raise ValidationError("Trade License file size must not exceed 5MB.")

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})