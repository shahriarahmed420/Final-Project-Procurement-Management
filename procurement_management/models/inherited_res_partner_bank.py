from odoo import api, fields, models


class BankAccountExtended(models.Model):
    _inherit = 'res.partner.bank'
    _description = 'Bank Account Extended'

    bank_address = fields.Text("Bank Address", required=True)