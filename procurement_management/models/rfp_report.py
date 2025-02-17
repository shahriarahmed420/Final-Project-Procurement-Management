from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import io
import xlsxwriter
from PIL import Image
from io import BytesIO

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
        return self.env.ref("procurement_management.action_rfp_qweb_report").report_action(self)

    def action_generate_excel_report(self):
        supplier = self.supplier_id
        if not supplier:
            raise UserError(_("Please select a supplier."))

        approved_rfqs = self.env["procurement_management.rfp"].search([
            ("approved_supplier_id", "=", supplier.id),
            ("status", "=", "accepted"),
            ("required_date", ">=", self.start_date),
            ("required_date", "<=", self.end_date),
        ])

        if not approved_rfqs:
            raise UserError(_("No approved RFPs found for this supplier within the selected date range."))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("RFP Report")

        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 40)
        worksheet.set_column("C:C", 40)
        worksheet.set_column("D:D", 30)

        company = self.env.company
        if not company.logo:
            raise UserError(
                _("The current company does not have a logo. Please add a logo before exporting the report."))

        logo_data = base64.b64decode(company.logo)
        logo_image = Image.open(io.BytesIO(logo_data))
        logo_image.thumbnail((120, 120))  # Resize logo to smaller size
        logo_buffer = BytesIO()
        logo_image.save(logo_buffer, format="PNG")
        logo_buffer.seek(0)

        worksheet.insert_image("A1", "company_logo.png", {"image_data": logo_buffer, "x_scale": 1, "y_scale": 1})

        start_row = 5
        worksheet.merge_range(f"A{start_row}:B{start_row}", supplier.name,
                              workbook.add_format(
                                  {"bold": True, "font_size": 14, "align": "center", "bg_color": "#D1E8E2"}))

        start_row += 2
        worksheet.write(f"A{start_row}", "Email",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#ADD8E6"}))
        worksheet.write(f"B{start_row}", supplier.email or "N/A", workbook.add_format({"border": 1}))
        worksheet.write(f"A{start_row + 1}", "Phone",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#ADD8E6"}))
        worksheet.write(f"B{start_row + 1}", supplier.phone or "N/A", workbook.add_format({"border": 1}))
        worksheet.write(f"A{start_row + 2}", "Address",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#ADD8E6"}))
        worksheet.write(f"B{start_row + 2}", supplier.contact_address or "N/A", workbook.add_format({"border": 1}))


        start_row += 4
        worksheet.write(f"A{start_row}", "Approved RFPs",
                        workbook.add_format({"bold": True, "font_size": 12, "bg_color": "#D9D9D9"}))

        start_row += 1
        # Write headers for the RFP table
        worksheet.write(f"A{start_row}", "RFP Number",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"B{start_row}", "RFP Date",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"C{start_row}", "Required Date",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"D{start_row}", "Total Amount",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))


        total_amount = 0
        row = start_row + 1
        for rfp in approved_rfqs:
            worksheet.write(row, 0, rfp.name, workbook.add_format({"border": 1}))
            worksheet.write(row, 1, rfp.create_date.strftime("%d/%m/%Y"), workbook.add_format({"border": 1}))
            worksheet.write(row, 2, rfp.required_date.strftime("%d/%m/%Y"), workbook.add_format({"border": 1}))
            worksheet.write(row, 3, rfp.total_amount, workbook.add_format({"border": 1, "num_format": "$#,##0.00"}))
            total_amount += rfp.total_amount
            row += 1

        worksheet.write(row, 2, "Total Amount", workbook.add_format({"bold": True, "border": 1, "bg_color": "#D9D9D9"}))
        worksheet.write(row, 3, total_amount,
                        workbook.add_format({"border": 1, "num_format": "$#,##0.00", "bg_color": "#D9D9D9"}))

        start_row = row + 3
        worksheet.write(f"A{start_row}", "Product Line Summary",
                        workbook.add_format({"bold": True, "font_size": 12, "bg_color": "#D9D9D9"}))
        start_row += 1

        worksheet.write(f"A{start_row}", "Product Name",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"B{start_row}", "Quantity",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"C{start_row}", "Unit Price",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"D{start_row}", "Delivery Charge",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"E{start_row}", "Subtotal",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))

        rfq_products = self.env["purchase.order.line"].search([
            ("order_id.rfp_id", "in", approved_rfqs.ids),
            ("order_id.state", "=", "purchase"),
        ])

        row = start_row + 1
        total_price = 0
        for line in rfq_products:
            worksheet.write(row, 0, line.product_id.name, workbook.add_format({"border": 1}))
            worksheet.write(row, 1, line.product_qty, workbook.add_format({"border": 1}))
            worksheet.write(row, 2, line.price_unit, workbook.add_format({"border": 1, "num_format": "$#,##0.00"}))
            worksheet.write(row, 3, line.delivery_charge, workbook.add_format({"border": 1, "num_format": "$#,##0.00"}))
            worksheet.write(row, 4, line.price_subtotal, workbook.add_format({"border": 1, "num_format": "$#,##0.00"}))
            total_price += line.price_subtotal
            row += 1

        worksheet.write(row, 3, "Total Price", workbook.add_format({"bold": True, "border": 1, "bg_color": "#D9D9D9"}))
        worksheet.write(row, 4, total_price,
                        workbook.add_format({"border": 1, "num_format": "$#,##0.00", "bg_color": "#D9D9D9"}))

        start_row = row + 3
        worksheet.write(f"A{start_row}", "Company Contact Information",
                        workbook.add_format({"bold": True, "font_size": 12, "bg_color": "#D9D9D9"}))
        start_row += 1

        worksheet.write(f"A{start_row}", "Email",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"B{start_row}", company.email, workbook.add_format({"border": 1}))
        worksheet.write(f"A{start_row + 1}", "Phone",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"B{start_row + 1}", company.phone, workbook.add_format({"border": 1}))
        worksheet.write(f"A{start_row + 2}", "Address",
                        workbook.add_format({"bold": True, "border": 1, "bg_color": "#B0E0E6"}))
        worksheet.write(f"B{start_row + 2}", company.partner_id.contact_address.replace("\n", ", "),
                        workbook.add_format({"border": 1}))

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': 'RFP_Report.xlsx',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
