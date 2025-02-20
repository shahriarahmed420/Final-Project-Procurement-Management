from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import ValidationError


class RFP(models.Model):
    _name = "procurement_management.rfp"
    _description = "Request for Purchase"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _log_access = True
    _rec_name = "name"

    name = fields.Char(string="RFP Number", required=True, copy=False, readonly=True, default=lambda self: _('New'))

    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        ('recommendation', 'Recommendation'),
        ('accepted', 'Accepted'),
    ], string="Status", default="draft", tracking=True)

    required_date = fields.Date(string="Required Date", default=lambda self: fields.Date.today() + timedelta(days=7), tracking=True)

    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    total_amount = fields.Monetary(string="Total Amount", currency_field="currency_id", compute="_compute_total_amount", store=True)

    reviewer_id = fields.Many2one('res.users', string="Reviewer", required=True, default=lambda self: self.env.user, tracking=True)
    approver_id = fields.Many2one('res.users', string="Approver", tracking=True)

    approved_supplier_id = fields.Many2one('res.partner', string="Approved Supplier", domain="[('id', 'in', recommended_supplier_ids), ('supplier_rank', '>', 0)]", tracking=True)
    recommended_supplier_ids = fields.Many2many('res.partner', string="Recommended Suppliers", compute="_compute_recommended_suppliers")

    product_line_ids = fields.One2many("procurement_management.rfp.product", "rfp_id", string="Product Lines")

    rfq_line_ids = fields.One2many("purchase.order", "rfp_id", string="RFQ Lines")

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, readonly=True)

    show_submit_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_recommend_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_return_draft_button = fields.Boolean(compute="_compute_button_visibility", store=False)

    show_approve_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_reject_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_close_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_accept_button = fields.Boolean(compute="_compute_button_visibility", store=False)


    @api.depends('rfq_line_ids.total_price')
    def _compute_total_amount(self):
        for rfp in self:
            rfp.total_amount = sum(rfp.rfq_line_ids.mapped('total_price') or [0.0])


    def _compute_recommended_suppliers(self):
        for rfp in self:
            recommended_rfq_lines = rfp.rfq_line_ids.filtered(lambda r: r.recommended)
            rfp.recommended_supplier_ids = recommended_rfq_lines.mapped('partner_id')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('procurement_management.rfp') or _('New')
        return super(RFP, self).create(vals)


    @api.depends("status")
    def _compute_button_visibility(self):
        for rfp in self:
            user = self.env.user
            is_reviewer = user.has_group("procurement_management.group_supplier_reviewer")
            is_approver = user.has_group("procurement_management.group_supplier_approver")

            rfp.show_submit_button = is_reviewer and not is_approver and rfp.status == "draft"
            rfp.show_recommend_button = is_reviewer and not is_approver and rfp.status == "closed"
            rfp.show_return_draft_button = is_reviewer and not is_approver and rfp.status == "submitted"

            rfp.show_approve_button = is_approver and not is_reviewer and rfp.status == "submitted"
            rfp.show_reject_button = is_approver and not is_reviewer and rfp.status == "submitted"
            rfp.show_close_button = is_approver and not is_reviewer and rfp.status == "approved"
            rfp.show_accept_button = is_approver and not is_reviewer and rfp.status == "recommendation"


    def send_rfp_submission_email(self):
        email_values = {
            'email_from': self.env.company.email or 'shahriar.ahmed@bjitacademy.com',
            'email_to': self.approver_id.email if self.approver_id else 'approver@yourcompany.com',
            'subject': f'New RFP {self.name} Submitted for Review',
            'body_html': f"""
                <p>Hello {self.approver_id.name},</p>
                <p>The RFP <b>{self.name}</b> has been submitted for review.</p>
                <p>To review this RFP, please <a href="#">click here</a>.</p>
                <p>Best regards,</p>
                <p>Your Procurement Team</p>
            """
        }
        self.env['mail.mail'].create(email_values).send()


    def action_submit(self):
        self.write({'status': 'submitted'})
        self.send_rfp_submission_email()

        approver_group = self.env.ref(
            'procurement_management.group_supplier_approver')
        for approver in approver_group.users:
            self.message_post(
                body=_("RFP <b>%s</b> has been submitted and is pending approval.") % self.name,
                partner_ids=[approver.partner_id.id]
            )


    def send_rfq_recommendation_email(self):
        email_values = {
            'email_from': self.env.company.email or 'shahriar.ahmed@bjitacademy.com',
            'email_to': self.approver_id.email if self.approver_id else 'approver@yourcompany.com',
            'subject': f'RFQ Recommended for RFP {self.name}',
            'body_html': f"""
                <p>Hello {self.approver_id.name},</p>
                <p>A recommended RFQ has been submitted for <b>RFP {self.name}</b>.</p>
                <p>Recommended Supplier: <b>{self.recommended_supplier_ids.name}</b></p>
                <p>To review this RFQ, please <a href="#">click here</a>.</p>
                <p>Best regards,</p>
                <p>Your Procurement Team</p>
            """
        }
        self.env['mail.mail'].create(email_values).send()


    def action_recommend(self):
        recommended_rfq = self.env['purchase.order'].search([
            ('rfp_id', '=', self.id),
            ('recommended', '=', True)
        ])

        if not recommended_rfq:
            raise ValidationError(_("You must have at least one recommended RFQ before proceeding."))

        # ✅ Allow multiple RFQs from different vendors, even if they belong to the same company
        for rfq in recommended_rfq:
            duplicate_rfqs = self.env['purchase.order'].search([
                ('rfp_id', '=', self.id),
                ('partner_id', '=', rfq.partner_id.id),  # Vendor-specific check, not company
                ('recommended', '=', True),
                ('id', '!=', rfq.id)  # Exclude the current record
            ])
            if duplicate_rfqs:
                print(f"⚠️ Multiple RFQs detected for vendor: {rfq.partner_id.name}, but allowed.")  # Debug log

        # ✅ Update RFQ State to 'sent'
        recommended_rfq.write({'state': 'sent'})

        # ✅ Ensure Correct Field Name for State Change
        self.write({'status': 'recommendation'})

        # ✅ Notify Approvers
        approver_group = self.env.ref('procurement_management.group_supplier_approver')
        for approver in approver_group.users:
            self.message_post(
                body=_("RFP <b>%s</b> has been recommended and is pending final approval.") % self.name,
                partner_ids=[approver.partner_id.id]
            )


    def action_return_draft(self):
        if self.status != 'submitted':
            raise ValidationError(_("You can only return an RFP to Draft when it's in the Submitted state."))

        self.write({'status': 'draft'})

        self.message_post(
            body=_("RFP <b>%s</b> has been returned to Draft for modifications.") % self.name,
            partner_ids=[self.create_uid.partner_id.id]  # Notify the creator
        )


    def send_rfp_approval_email(self):
        email_values = {
            'email_from': self.env.company.email or 'shahriar.ahmed@bjitacademy.com',
            'email_to': self.reviewer_id.email if self.reviewer_id else 'reviewer@yourcompany.com',
            'subject': f'RFP {self.name} Approved',
            'body_html': f"""
                <p>Hello {self.reviewer_id.name},</p>
                <p>Your RFP <b>{self.name}</b> has been approved.</p>
                <p>Suppliers can now submit their quotations.</p>
                <p>Best regards,</p>
                <p>Your Procurement Team</p>
            """
        }
        self.env['mail.mail'].create(email_values).send()


    def action_approve(self):
        self.write({'status': 'approved'})

        # Notify Reviewer
        if self.reviewer_id:
            self.message_post(
                body=_("RFP <b>%s</b> has been Approved.") % self.name,
                partner_ids=[self.reviewer_id.partner_id.id]
            )

        supplier_group = self.env.ref("base.group_portal")
        for supplier in supplier_group.users:
            self.message_post(
                body=_("A new RFP <b>%s</b> is now open for quotations.") % self.name,
                partner_ids=[supplier.partner_id.id]
            )

        self.send_rfp_approval_email()


    def action_reject(self):
        self.write({'status': 'rejected'})

        if self.reviewer_id:
            self.message_post(
                body=_("RFP <b>%s</b> has been Rejected.") % self.name,
                partner_ids=[self.reviewer_id.partner_id.id]
            )


    def send_rfp_closure_email(self):
        """ Send email notification when an RFP is closed """
        email_values = {
            'email_from': self.env.company.email or 'shahriar.ahmed@bjitacademy.com',
            'email_to': ','.join(self.rfq_line_ids.recommended_supplier_ids.mapped('email')),
            'subject': f'RFP {self.name} is Now Closed',
            'body_html': f"""
                <p>Hello,</p>
                <p>The RFP <b>{self.name}</b> has been closed.</p>
                <p>No more RFQs will be accepted for this RFP.</p>
                <p>Best regards,</p>
                <p>Your Procurement Team</p>
            """
        }
        self.env['mail.mail'].create(email_values).send()


    def action_close(self):
        if self.status != 'approved':
            raise ValidationError(_("Only approved RFPs can be closed."))
        self.write({'status': 'closed'})
        self.message_post(body=_("RFP <b>%s</b> has been Closed.") % self.name)
        self.send_rfp_closure_email()


    def send_rfq_approval_email(self):
        """ Send email notification when an RFQ is approved """
        email_values = {
            'email_from': self.env.company.email or 'shahriar.ahmed@bjitacademy.com',
            'email_to': self.recommended_supplier_ids.email if self.recommended_supplier_ids else 'supplier@yourcompany.com',
            'subject': f'Your RFQ has been Approved for RFP {self.name}',
            'body_html': f"""
                <p>Hello {self.recommended_supplier_ids.name},</p>
                <p>Your RFQ for <b>RFP {self.name}</b> has been approved.</p>
                <p>A purchase order has been created based on your quotation.</p>
                <p>To view details, <a href="#">click here</a>.</p>
                <p>Best regards,</p>
                <p>Your Procurement Team</p>
            """
        }
        self.env['mail.mail'].create(email_values).send()

    def action_accept(self):
        self.ensure_one()  # Ensure only one RFP is being processed

        # ✅ Fetch the RFQ marked as selected
        selected_rfq = self.env['purchase.order'].sudo().search([
            ('rfp_id', '=', self.id),
            ('is_selected', '=', True),  # ✅ Identify the selected RFQ
            ('state', '=', 'sent')
        ], limit=1)

        if not selected_rfq:
            raise ValidationError(_("You must select an RFQ before accepting."))

        # ✅ Step 1: Convert Selected RFQ to a Purchase Order
        selected_rfq.sudo().write({
            'state': 'purchase'  # ✅ "state" is the correct field, not "status"
        })

        self.sudo().write({
            'status': 'accepted',  # ✅ Ensure this field exists in "rfp"
            'approved_supplier_id': selected_rfq.partner_id.id
        })

        # ✅ Step 2: Cancel All Other RFQs for this RFP
        other_rfqs = self.env['purchase.order'].sudo().search([
            ('rfp_id', '=', self.id),
            ('id', '!=', selected_rfq.id),
            ('state', '=', 'sent')
        ])

        for rfq in other_rfqs:
            rfq.sudo().write({
                'state': 'cancel'  # ✅ Use "state" instead of "status"
            })
            rfq.message_post(body=_("This RFQ has been canceled because another RFQ was accepted."))


        self.message_post(body=_("RFP <b>%s</b> has been accepted and converted into a Purchase Order.") % self.name)

        # ✅ Debugging Output
        print(f"✅ Accepted RFQ: {selected_rfq.name} (Converted to Purchase Order)")
        for rfq in other_rfqs:
            print(f"🚨 Rejected RFQ: {rfq.name} (Canceled)")