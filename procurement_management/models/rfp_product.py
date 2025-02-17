from odoo import models, fields, api

class RFPProduct(models.Model):
    _name = "procurement_management.rfp.product"
    _description = "RFP Product Line"

    rfp_id = fields.Many2one("procurement_management.rfp", string="RFP Reference", ondelete="cascade")  # ✅ Keep only RFP reference

    product_id = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Text(string="Description")
    quantity = fields.Integer(string="Quantity", required=True)
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id")
    subtotal_price = fields.Monetary(string="Subtotal", compute="_compute_subtotal", store=True)
    delivery_charges = fields.Monetary(string="Delivery Charges", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends("quantity", "unit_price", "delivery_charges")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal_price = (line.quantity * line.unit_price) + (line.delivery_charges or 0.0)