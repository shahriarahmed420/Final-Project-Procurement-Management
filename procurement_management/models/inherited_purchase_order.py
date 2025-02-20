from odoo import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('procurement_management.rfp', string='Linked RFP', readonly=True)
    expected_delivery_date = fields.Date()
    terms_conditions = fields.Html(string='Terms & Conditions')
    warranty_period = fields.Integer(string='Warranty (Months)')
    score = fields.Integer()
    recommended = fields.Boolean()
    rfp_status = fields.Selection(related='rfp_id.status', store=True, string="RFP Status")
    is_selected = fields.Boolean(string="Selected RFQ", help="Flag to determine which RFQ was selected.")

    total_price = fields.Monetary(string="Total Price", compute="_compute_total_price", store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    partner_id = fields.Many2one('res.partner', string="Vendor", required=True)
    user_id = fields.Many2one('res.users', string="Buyer", default=lambda self: self.env.user, required=True)

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string="Status", default="draft", tracking=True)


    def open_form_view(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }


    @api.depends("order_line.price_total")
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(order.order_line.mapped("price_total"))


    def send_rfq_submission_email(self):
        email_values = {
            'email_from': self.env.company.email or 'shahriar.ahmed@bjitacademy.com',
            'email_to': self.rfp_id.reviewer_id.email if self.rfp_id.reviewer_id else 'reviewer@yourcompany.com',
            'subject': f'New RFQ Submitted for RFP {self.rfp_id.name}',
            'body_html': f"""
                <p>Hello {self.rfp_id.reviewer_id.name},</p>
                <p>A new RFQ has been submitted for <b>RFP {self.rfp_id.name}</b>.</p>
                <p>Supplier: <b>{self.partner_id.name}</b></p>
                <p>To review this RFQ, please <a href="#">click here</a>.</p>
                <p>Best regards,</p>
                <p>Your Procurement Team</p>
            """
        }
        self.env['mail.mail'].create(email_values).send()


    def action_submit_rfq(self):
        self.write({'state': 'draft'})
        self.send_rfq_submission_email()


    def action_approve_rfq(self):
        self.write({'state': 'purchase'})


    def action_accept(self):
        print('action accept')
        self.rfp_id.status = 'accepted'
        rfq = self.env['purchase.order'].search([('rfp_id', '=', self.id)])
        rfq.button_confirm()


    @api.constrains('recommended', 'partner_id', 'rfp_id')
    def _check_unique_recommended_per_supplier(self):
        for order in self:
            if order.recommended:
                existing_recommended = self.search([
                    ('rfp_id', '=', order.rfp_id.id),
                    ('partner_id', '=', order.partner_id.id),
                    ('recommended', '=', True),
                    ('id', '!=', order.id)  # Exclude the current record in case of updates
                ])
                if existing_recommended:
                    raise exceptions.ValidationError(_(
                        f"A company {order.partner_id.name} cannot have more than one recommended RFQ for the same RFP {order.rfp_id.name}."
                    ))