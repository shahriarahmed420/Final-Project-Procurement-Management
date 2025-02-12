from odoo import models, fields, api, exceptions,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('procurement_management.rfp', string='Linked RFP', readonly=True)
    expected_delivery_date = fields.Date()
    terms_conditions = fields.Html(string='Terms & Conditions')
    warranty_period = fields.Integer(string='Warranty (Months)')
    score = fields.Integer()
    recommended = fields.Boolean()
    rfp_status = fields.Selection(related='rfp_id.status', store=True, string="RFP Status")

    total_price = fields.Monetary(string="Total Price", compute="_compute_total_price", store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends("order_line.price_total")
    def _compute_total_price(self):
        """Computes the total price from order lines (product prices + delivery charges)."""
        for order in self:
            order.total_price = sum(order.order_line.mapped("price_total"))

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
