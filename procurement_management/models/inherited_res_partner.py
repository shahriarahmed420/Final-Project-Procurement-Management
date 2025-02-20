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
    ], string="Company Type")
    trade_license_no = fields.Char("Trade License Number")
    commencement_date = fields.Date("Commencement Date")
    expiry_date = fields.Date("Expiry Date")
    tax_id_num = fields.Char("Tax Identification Number (TIN)")
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