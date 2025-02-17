from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    rfp_ids = fields.One2many('procurement_management.rfp', 'approved_supplier_id', string="Approved RFPs")