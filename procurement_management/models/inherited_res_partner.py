from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = 'Supplier Registration'

    rfp_ids = fields.One2many('procurement_management.rfp', 'approved_supplier_id', string="Approved RFPs")

    company_address = fields.Char("Company Address")
    company_type_category = fields.Selection([
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
    ], string="Company Type Category")

    child_ids = fields.One2many('res.partner', 'parent_id', string="Client References")

    primary_contact_name = fields.Char("Primary Contact Name")
    primary_contact_email = fields.Char("Primary Contact Email")
    primary_contact_phone = fields.Char("Primary Contact Phone")

    finance_contact_name = fields.Char("Finance Contact Name")
    finance_contact_email = fields.Char("Finance Contact Email")
    finance_contact_phone = fields.Char("Finance Contact Phone")

    authorized_contact_name = fields.Char("Authorized Contact Name")
    authorized_contact_email = fields.Char("Authorized Contact Email")
    authorized_contact_phone = fields.Char("Authorized Contact Phone")

    trade_license_no = fields.Char("Trade License Number")
    vat = fields.Char("Tax Identification Number (TIN)", size=16)
    commencement_date = fields.Date("Commencement Date")

    certificate_expiry_date = fields.Date("Certificate Expiry Date")
    certification_name = fields.Char("Certification Name")
    certificate_number = fields.Char("Certificate Number")
    certifying_body = fields.Char("Certifying Body")
    award_date = fields.Date("Award Date")
    certificate_expiry_date = fields.Date("Expiry Date")

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

    client_1_name = fields.Char("Client 1 Name")
    client_1_email = fields.Char("Client 1 Email")
    client_1_phone = fields.Char("Client 1 Phone")
    client_1_address = fields.Text("Client 1 Address")

    client_2_name = fields.Char("Client 2 Name")
    client_2_email = fields.Char("Client 2 Email")
    client_2_phone = fields.Char("Client 2 Phone")
    client_2_address = fields.Text("Client 2 Address")

    client_3_name = fields.Char("Client 3 Name")
    client_3_email = fields.Char("Client 3 Email")
    client_3_phone = fields.Char("Client 3 Phone")
    client_3_address = fields.Text("Client 3 Address")

    client_4_name = fields.Char("Client 4 Name")
    client_4_email = fields.Char("Client 4 Email")
    client_4_phone = fields.Char("Client 4 Phone")
    client_4_address = fields.Text("Client 4 Address")

    client_5_name = fields.Char("Client 5 Name")
    client_5_email = fields.Char("Client 5 Email")
    client_5_phone = fields.Char("Client 5 Phone")
    client_5_address = fields.Text("Client 5 Address")