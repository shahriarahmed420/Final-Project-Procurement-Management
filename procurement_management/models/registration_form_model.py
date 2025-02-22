from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class RegistrationForm(models.Model):
    _name = 'registration.form'
    _description = 'A model to view and track for supplier form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

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

    client_name = fields.Char("Client Name")
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
    submission_date = fields.Date(string="Submission Date", required=True, default=fields.Date.context_today)

    # extra necessary fields after 5 sections

    status = fields.Selection([
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('blacklisted', 'Blacklisted')
    ], default='submitted', tracking=True)

    reviewer_id = fields.Many2one(
        'res.users',
        string="Reviewer",
        domain=lambda self: [('groups_id', 'in', self.env.ref('procurement_management.group_supplier_reviewer').ids)],
        tracking=True
    )

    approver_id = fields.Many2one(
        'res.users',
        string="Approver",
        domain=lambda self: [('groups_id', 'in', self.env.ref('procurement_management.group_supplier_approver').ids)],
        tracking=True
    )

    rejection_reason = fields.Text(string="Rejection Reason")
    blacklist_reason = fields.Text(string="Blacklist Reason")
    review_comments = fields.Text(string="Reviewer Comments")
    approval_comments = fields.Text(string="Approver Comments")

    def action_review_approve(self):
        if not self.reviewer_id:
            raise ValidationError(_("A reviewer must be assigned before approval."))
        self.write({'status': 'under_review'})
        self.message_post(body=_("Application has been forwarded to the approver."))


    def action_final_approve(self):
        if not self.approver_id:
            raise ValidationError(_("An approver must be assigned before final approval."))

        existing_user = self.env['res.users'].sudo().search([('login', '=', self.email)], limit=1)
        if existing_user:
            self.message_post(body=_("User account already exists for supplier: %s" % self.email))
        else:
            self.create_supplier_user()

        self.create_vendor_record()
        self.send_supplier_approval_email()
        self.write({'status': 'approved'})
        self.message_post(body=_("Supplier application approved, vendor created, and user assigned."))


    def action_reject(self):
        if not self.rejection_reason:
            raise ValidationError(_("Please provide a reason for rejection."))
        self.write({'status': 'rejected'})
        self.send_rejection_email()
        self.message_post(body=_("Application rejected: %s" % self.rejection_reason))


    def action_blacklist(self):
        if not self.blacklist_reason:
            raise ValidationError(_("Please provide a reason for blacklisting."))
        self.write({'status': 'blacklisted'})
        self.send_rejection_email()
        self.message_post(body=_("Supplier blacklisted: %s" % self.blacklist_reason))


    def create_vendor_record(self):
        default_reviewer = self.env.ref("procurement_management.group_supplier_reviewer").users[:1]

        user = self.env['res.users'].sudo().search([('login', '=', self.email)], limit=1)

        existing_partner = self.env['res.partner'].sudo().search([('email', '=', self.email)], limit=1)

        if not existing_partner:
            # Create the vendor record if partner doesn't exist
            vendor = self.env['res.partner'].create({
                'name': self.company_name,
                'is_company': True,
                'company_type': 'company',
                'email': self.email,
                'phone': self.primary_contact_phone,
                'supplier_rank': 1,
                'user_ids': [(4, user.id)] if user else [],
                'company_id': self.env.company.id,
            })
        else:
            # If partner exists, assign the existing partner to vendor
            vendor = existing_partner
            if vendor.supplier_rank != 1:
                vendor.sudo().write({
                    'supplier_rank': 1  # Ensure supplier_rank is set to 1
                })

        existing_bank = self.env['res.bank'].sudo().search([
            ('name', '=', self.bank_name),
            ('bic', '=', self.bank_swift_code)
        ], limit=1)

        if not existing_bank and self.bank_name:
            existing_bank = self.env['res.bank'].create({
                'name': self.bank_name,
                'street': self.bank_address,
                'bic': self.bank_swift_code,
                'iban': self.iban,
            })

        existing_bank_entry = self.env['res.partner.bank'].sudo().search_count([
            ('partner_id', '=', vendor.id),
            ('bank_id', '=', existing_bank.id if existing_bank else False),
            ('acc_number', '=', self.account_number),
        ])

        if not existing_bank_entry:
            self.env['res.partner.bank'].create({
                'partner_id': vendor.id,
                'bank_id': existing_bank.id,
                'acc_number': self.account_number,
                'acc_holder_name': self.account_name,
                'bank_address': self.bank_address,
            })

        self.write({
            'status': 'submitted',
            'reviewer_id': default_reviewer.id if default_reviewer else False
        })

        self.message_post(body=_("Vendor Record Created: %s with Bank Details" % vendor.name))


    def create_supplier_user(self):
        portal_group = self.env.ref('base.group_portal')
        existing_user = self.env['res.users'].sudo().search([('login', '=', self.email)], limit=1)

        if existing_user:
            self.message_post(body=_("User already exists for supplier: %s" % self.email))
            return

        supplier_partner = self.env['res.partner'].sudo().search([('email', '=', self.email)], limit=1)
        if not supplier_partner:
            supplier_partner = self.env['res.partner'].sudo().create({
                'name': self.company_name,
                'email': self.email,
                'company_id': self.env.company.id,
            })

        user = self.env['res.users'].sudo().create({
            'name': self.company_name,
            'login': self.email,
            'email': self.email,
            'password': self.email,
            'partner_id': supplier_partner.id,
            'company_id': self.env.company.id,
            'groups_id': [(6, 0, [portal_group.id])]
        })
        self.message_post(body=_("Portal user account created for supplier: %s" % user.login))


    @api.constrains('certificate_expiry_date')
    def _check_certificate_expiry(self):
        for record in self:
            if record.certificate_expiry_date and record.certificate_expiry_date <= fields.Date.today():
                raise ValidationError("Certificate expiry date must be in the future.")


    @api.constrains(
        'trade_license_business_registration', 'certificate_of_incorporation', 'certificate_of_good_standing',
        'establishment_card', 'vat_tax_certificate', 'memorandum_of_association',
        'identification_document_for_authorized_person', 'bank_letter_indicating_bank_account',
        'past_2_years_audited_financial_statements', 'other_certifications'
    )
    def _check_file_size(self):
        max_size = 5 * 1024 * 1024  # 5 MB
        for field in self._fields:
            if self[field] and isinstance(self[field], bytes) and len(self[field]) > max_size:
                raise ValidationError(f"The file size for {self._fields[field].string} must not exceed 5MB.")