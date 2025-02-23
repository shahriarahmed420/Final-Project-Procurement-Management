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

    primary_contact_name = fields.Char("Primary Contact Name", required=True)
    primary_contact_email = fields.Char("Primary Contact Email", required=True)
    primary_contact_phone = fields.Char("Primary Contact Phone", required=True)
    primary_contact_address = fields.Text("Primary Contact Address")

    finance_contact_name = fields.Char("Finance Contact Name", required=True)
    finance_contact_email = fields.Char("Finance Contact Email", required=True)
    finance_contact_phone = fields.Char("Finance Contact Phone", required=True)
    finance_contact_address = fields.Text("Finance Contact Address")

    authorized_contact_name = fields.Char("Authorized Contact Name", required=True)
    authorized_contact_email = fields.Char("Authorized Contact Email", required=True)
    authorized_contact_phone = fields.Char("Authorized Contact Phone", required=True)
    authorized_contact_address = fields.Char("Authorized Contact Address")

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

    reviewer_comments = fields.Text(string="Reviewer Comments")

    @api.constrains('status', 'reviewer_comments')
    def _check_review_comments_required(self):
        for record in self:
            if record.status in ['reject', 'blacklist'] and not record.reviewer_comments:
                raise ValidationError(_("Comments are required when rejecting or blacklisting a supplier."))


    @api.constrains(
        'client_1_name', 'client_1_email', 'client_1_phone', 'client_1_address', 'client_2_name', 'client_2_email', 'client_2_phone',
        'client_2_address', 'client_3_name', 'client_3_email', 'client_3_phone', 'client_3_address', 'client_4_name', 'client_4_email',
        'client_4_phone', 'client_4_address', 'client_5_name', 'client_5_email', 'client_5_phone', 'client_5_address'
    )
    def _check_client_name_required(self):
        for record in self:
            for i in range(1, 6):  # Loop over client 1 to 5
                email = getattr(record, f'client_{i}_email')
                phone = getattr(record, f'client_{i}_phone')
                address = getattr(record, f'client_{i}_address')
                name = getattr(record, f'client_{i}_name')

                # If any of Email, Phone, or Address is provided, Name must be mandatory
                if (email or phone or address) and not name:
                    raise ValidationError(f"Client {i}: Name is required when Email, Phone, or Address is provided.")


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
        self.write({'status': 'approved'})
        self.message_post(body=_("Supplier application approved, vendor created, and user assigned."))

        email_values = {
            'email_from': 'shahriar.ahmed@bjitacademy.com',
            'email_to': self.email,
            'subject': 'Your Supplier Application Update',
            'body_html': f'<p>Your have been registered and approved as a supplier.</p>'
        }

        mail = self.env['mail.mail'].sudo().create(email_values)
        mail.sudo().send()


    def action_reject(self):
        if not self.rejection_reason:
            raise ValidationError(_("Please provide a reason for rejection."))
        self.write({'status': 'rejected'})
        self.send_rejection_email()
        self.message_post(body=_("Application rejected: %s" % self.rejection_reason))


    def action_blacklist(self):
        if not self.reviewer_comments:
            raise ValidationError(_("Please provide a reason for blacklisting."))
        self.write({'status': 'blacklisted'})
        self.send_rejection_email()
        self.message_post(body=_("Supplier blacklisted: %s" % self.reviewer_comments))


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

                'primary_contact_name': self.primary_contact_name,
                'primary_contact_email': self.primary_contact_email,
                'primary_contact_phone': self.primary_contact_phone,

                'finance_contact_name': self.finance_contact_name,
                'finance_contact_email': self.finance_contact_email,
                'finance_contact_phone': self.finance_contact_phone,

                'authorized_contact_name': self.authorized_contact_name,
                'authorized_contact_email': self.authorized_contact_email,
                'authorized_contact_phone': self.authorized_contact_phone,

                'trade_license_no': self.trade_license_no,
                'vat': self.tax_id_num,

                'certification_name': self.certification_name,
                'certificate_number': self.certificate_number,
                'certifying_body': self.certifying_body,
                'award_date': self.award_date,
                'certificate_expiry_date': self.certificate_expiry_date,
            })
        else:
            # If partner exists, assign the existing partner to vendor
            vendor = existing_partner
            if vendor.supplier_rank != 1:
                vendor.sudo().write({
                    'supplier_rank': 1,  # Ensure supplier_rank is set to 1
                    'phone': self.primary_contact_phone,
                    'vat': self.tax_id_num,
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

        client_data = [
            {'name': self.client_1_name, 'email': self.client_1_email, 'phone': self.client_1_phone,
             'street': self.client_1_address},
            {'name': self.client_2_name, 'email': self.client_2_email, 'phone': self.client_2_phone,
             'street': self.client_2_address},
            {'name': self.client_3_name, 'email': self.client_3_email, 'phone': self.client_3_phone,
             'street': self.client_3_address},
            {'name': self.client_4_name, 'email': self.client_4_email, 'phone': self.client_4_phone,
             'street': self.client_4_address},
            {'name': self.client_5_name, 'email': self.client_5_email, 'phone': self.client_5_phone,
             'street': self.client_5_address},
        ]

        client_values = [(0, 0, client) for client in client_data if client["name"]]

        if client_values:
            vendor.write({'child_ids': client_values})

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