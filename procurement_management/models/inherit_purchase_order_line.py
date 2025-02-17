from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    delivery_charge = fields.Monetary(string='Delivery Charge', default=0.0)

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'delivery_charge')
    def _compute_amount(self):
        """Compute total price including taxes and delivery charges."""
        for line in self:
            # ✅ Calculate subtotal excluding tax
            amount_untaxed = (line.product_qty * line.price_unit)

            # ✅ Compute Taxes (Odoo's Standard Method)
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = next(iter(tax_results['totals'].values()))
            amount_tax = totals['amount_tax']

            # ✅ Ensure the total price includes the delivery charge
            line.update({
                'price_subtotal': amount_untaxed + line.delivery_charge,  # Include delivery charge in subtotal
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax + line.delivery_charge,  # Include in total
            })
