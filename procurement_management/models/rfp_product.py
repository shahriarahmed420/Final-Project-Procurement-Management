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

    @api.depends("rfp_id", "product_id")
    def _compute_prices(self):
        """Fetch Unit Price and Delivery Charges from the related RFQ Purchase Order Line."""
        for line in self:
            purchase_line = self.env["purchase.order.line"].search([
                ("order_id.rfp_id", "=", line.rfp_id.id),
                ("product_id", "=", line.product_id.id),
            ], limit=1)

            if purchase_line:
                line.unit_price = purchase_line.price_unit or 0.0
                line.delivery_charges = purchase_line.delivery_charge or 0.0
            else:
                line.unit_price = 0.0
                line.delivery_charges = 0.0