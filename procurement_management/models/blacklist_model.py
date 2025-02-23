from email.policy import default

from odoo import models, fields, api

class SupplierBlacklist(models.Model):
    _name = 'supplier.blacklist'
    _description = 'Supplier Blacklist'

    email = fields.Char()
    reason = fields.Text()
    blacklist = fields.Boolean(default=True)

    @api.model
    def is_blacklisted(self, email):
        return bool(self.sudo().search([('email', '=', email), ('blacklisted', '=', 'True')], limit=1))