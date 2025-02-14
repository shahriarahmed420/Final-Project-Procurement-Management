from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RFPReport(models.TransientModel):
    _name = "procurement_management.rfp.report"
    _description = "RFP Report"

    supplier_id = fields.Many2one('res.partner', string="Supplier", required=True, domain="[('supplier_rank', '>', 0)]")
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_("Start date can not be bigger than the End date"))

    def action_generate_qweb_report(self):
        # return self.env.ref("procurement_management.action_rfp_qweb_report").report_action(self)
        pass

    def action_generate_excel_report(self):
        # return self.env.ref("procurement_management.action_rfp_excel_report").report_action(self)
        pass