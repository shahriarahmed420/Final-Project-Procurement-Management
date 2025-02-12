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
        ('under_review', 'Under Review'),
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

    approved_supplier_id = fields.Many2one('res.partner', string="Approved Supplier", domain="[('id', 'in', recommended_supplier_ids)]", tracking=True)
    recommended_supplier_ids = fields.Many2many('res.partner', string="Recommended Suppliers", compute="_compute_recommended_suppliers")

    product_line_ids = fields.One2many("procurement_management.rfp.product", "rfp_id", string="Product Lines")

    rfq_line_ids = fields.One2many("purchase.order", "rfp_id", string="RFQ Lines")

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, readonly=True)

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


    show_submit_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_recommend_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_return_draft_button = fields.Boolean(compute="_compute_button_visibility", store=False)

    show_approve_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_reject_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_close_button = fields.Boolean(compute="_compute_button_visibility", store=False)
    show_accept_button = fields.Boolean(compute="_compute_button_visibility", store=False)

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

    def action_submit(self):
        self.write({'status': 'submitted'})

        approver_group = self.env.ref(
            'procurement_management.group_supplier_approver')
        for approver in approver_group.users:
            self.message_post(
                body=_("RFP <b>%s</b> has been submitted and is pending approval.") % self.name,
                partner_ids=[approver.partner_id.id]
            )

    def action_recommend(self):
        recommended_rfq = self.env['purchase.order'].search([('rfp_id', '=', self.id), ('recommended', '=', True)])

        if not recommended_rfq:
            raise ValidationError(_("You must have at least one recommended RFQ before proceeding."))

        self.write({'status': 'recommendation'})

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

    def action_approve(self):
        """ Approves the RFP, Notifies the Reviewer & Suppliers """
        self.write({'status': 'approved'})

        # Notify Reviewer
        if self.reviewer_id:
            self.message_post(
                body=_("RFP <b>%s</b> has been Approved.") % self.name,
                partner_ids=[self.reviewer_id.partner_id.id]
            )

        # Notify Suppliers about New RFP
        supplier_group = self.env.ref("base.group_portal")
        for supplier in supplier_group.users:
            self.message_post(
                body=_("A new RFP <b>%s</b> is now open for quotations.") % self.name,
                partner_ids=[supplier.partner_id.id]
            )

    def action_reject(self):
        """ Rejects the RFP and notifies the Reviewer """
        self.write({'status': 'rejected'})

        # Notify Reviewer
        if self.reviewer_id:
            self.message_post(
                body=_("RFP <b>%s</b> has been Rejected.") % self.name,
                partner_ids=[self.reviewer_id.partner_id.id]
            )

    def action_close(self):
        """ Closes the RFP and removes it from the portal """
        self.write({'status': 'closed'})
        self.message_post(body=_("RFP <b>%s</b> has been Closed.") % self.name)

    def action_accept(self):
        """ Accepts the recommended RFQ and converts it into a PO """
        recommended_rfq = self.env['purchase.order'].search([('rfp_id', '=', self.id), ('recommended', '=', True)],
                                                            limit=1)

        if not recommended_rfq:
            raise ValidationError(_("There must be a recommended RFQ before accepting the RFP."))

        self.write({'status': 'accepted'})

        # ✅ Create a Purchase Order (PO) from the Approved RFQ
        po_values = {
            'partner_id': recommended_rfq.partner_id.id,
            'rfp_id': self.id,
            'date_order': fields.Date.today(),
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_qty': line.product_qty,
                'price_unit': line.price_unit,
            }) for line in recommended_rfq.order_line],
        }

        po = self.env['purchase.order'].create(po_values)
        self.message_post(body=_("RFP <b>%s</b> has been accepted and a Purchase Order <b>%s</b> has been created.") % (
        self.name, po.name))