from odoo import models, fields, api


class procurement_management(models.Model):
    _name = 'procurement_management.procurement_management'
    _description = 'procurement_management.procurement_management'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100