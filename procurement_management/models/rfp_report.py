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

        # Define column widths
        worksheet.set_column("A:A", 22)
        worksheet.set_column("B:B", 35)
        worksheet.set_column("C:C", 28)
        worksheet.set_column("D:D", 30)
        worksheet.set_column("E:E", 30)

        # Define refined styles
        soft_blue_header = workbook.add_format(
            {"bold": True, "border": 1, "bg_color": "#005f73", "font_color": "white", "align": "center"})
        deep_teal_header = workbook.add_format(
            {"bold": True, "border": 1, "bg_color": "#0a9396", "font_color": "white", "align": "center"})
        title_format = workbook.add_format(
            {"bold": True, "font_size": 13, "bg_color": "#005f73", "font_color": "white", "border": 1,
             "align": "center"})
        bold_center = workbook.add_format(
            {"bold": True, "align": "center", "font_size": 14, "bg_color": "#94d2bd", "border": 1})
        alt_row_format = workbook.add_format(
            {"border": 1, "bg_color": "#f0fdfa", "align": "center"})  # Light pastel blue
        cell_format = workbook.add_format({"border": 1, "align": "center", "font_color": "#3d405b"})  # Modern gray font
        currency_format = workbook.add_format(
            {"border": 1, "num_format": "$#,##0.00", "align": "center", "font_color": "#3d405b"})
        highlight_total = workbook.add_format(
            {"bold": True, "border": 1, "bg_color": "#0a9396", "font_color": "white", "align": "center"})

        company = self.env.company
        if not company.logo:
            raise UserError(
                _("The current company does not have a logo. Please add a logo before exporting the report."))

        # Remove any unwanted highlight in the top-left cell
        worksheet.write("A1", "", workbook.add_format({"bg_color": "#FFFFFF"}))

        # Insert Logo aligned with Vendor Info
        logo_data = base64.b64decode(company.logo)
        logo_image = Image.open(io.BytesIO(logo_data))
        logo_image.thumbnail((120, 120))
        logo_buffer = io.BytesIO()
        logo_image.save(logo_buffer, format="PNG")
        logo_buffer.seek(0)
        worksheet.insert_image("A5", "company_logo.png", {"image_data": logo_buffer, "x_scale": 1, "y_scale": 1})

        # Vendor Name (Centered Title)
        worksheet.merge_range("B5:D5", supplier.name, bold_center)

        # Vendor Information Section
        vendor_info_start = 7
        vendor_fields = ["Email", "Phone", "Address", "TIN", "Bank", "Account Name", "Account Number"]
        vendor_values = [
            supplier.email or "N/A", supplier.phone or "N/A", supplier.contact_address or "N/A",
            supplier.vat or "N/A",
            supplier.bank_ids.mapped("bank_id.name")[0] if supplier.bank_ids else "N/A",
            supplier.bank_ids.mapped("acc_holder_name")[0] if supplier.bank_ids else "N/A",
            supplier.bank_ids.mapped("acc_number")[0] if supplier.bank_ids else "N/A"
        ]

        for i, field in enumerate(vendor_fields):
            worksheet.write(f"B{vendor_info_start + i}", field, deep_teal_header)
            worksheet.write(f"C{vendor_info_start + i}", vendor_values[i], cell_format)

        # Approved RFPs Section
        rfp_start = vendor_info_start + len(vendor_fields) + 2
        worksheet.merge_range(f"A{rfp_start}:D{rfp_start}", "Approved RFPs", title_format)
        worksheet.write(f"A{rfp_start + 1}", "RFP Number", soft_blue_header)
        worksheet.write(f"B{rfp_start + 1}", "RFP Date", soft_blue_header)
        worksheet.write(f"C{rfp_start + 1}", "Required Date", soft_blue_header)
        worksheet.write(f"D{rfp_start + 1}", "Total Amount", soft_blue_header)

        row = rfp_start + 2
        total_rfp_amount = 0
        for index, rfp in enumerate(approved_rfqs):
            row_format = alt_row_format if index % 2 == 0 else cell_format
            worksheet.write(row, 0, rfp.name, row_format)
            worksheet.write(row, 1, rfp.create_date.strftime("%d/%m/%Y"), row_format)
            worksheet.write(row, 2, rfp.required_date.strftime("%d/%m/%Y"), row_format)
            worksheet.write(row, 3, rfp.total_amount, currency_format)
            total_rfp_amount += rfp.total_amount
            row += 1

        worksheet.write(row, 2, "Total", highlight_total)
        worksheet.write(row, 3, total_rfp_amount, currency_format)

        # Product Line Summary
        product_start = row + 3
        worksheet.merge_range(f"A{product_start}:E{product_start}", "Product Line Summary", title_format)
        worksheet.write(f"A{product_start + 1}", "Product Name", soft_blue_header)
        worksheet.write(f"B{product_start + 1}", "Quantity", soft_blue_header)
        worksheet.write(f"C{product_start + 1}", "Unit Price", soft_blue_header)
        worksheet.write(f"D{product_start + 1}", "Delivery Charge", soft_blue_header)
        worksheet.write(f"E{product_start + 1}", "Subtotal", soft_blue_header)

        rfq_products = self.env["purchase.order.line"].search([
            ("order_id.rfp_id", "in", approved_rfqs.ids),
            ("order_id.state", "=", "purchase"),
        ])

        row = product_start + 2
        total_price = 0
        for index, line in enumerate(rfq_products):
            row_format = alt_row_format if index % 2 == 0 else cell_format
            worksheet.write(row, 0, line.product_id.name, row_format)
            worksheet.write(row, 1, line.product_qty, row_format)
            worksheet.write(row, 2, line.price_unit, currency_format)
            worksheet.write(row, 3, line.delivery_charge, currency_format)
            worksheet.write(row, 4, line.price_subtotal, currency_format)
            total_price += line.price_subtotal
            row += 1

        worksheet.write(row, 3, "Total Price", highlight_total)
        worksheet.write(row, 4, total_price, currency_format)

        # Company Contact Information (Spans 3 Columns)
        contact_start = row + 3
        worksheet.merge_range(f"A{contact_start}:C{contact_start}", "Company Contact Information", title_format)
        contact_fields = ["Email", "Phone", "Address"]
        contact_values = [
            company.email,
            company.phone,
            company.partner_id.contact_address.replace("\n", ", ")
        ]

        for i, field in enumerate(contact_fields):
            worksheet.write(f"A{contact_start + 1 + i}", field, deep_teal_header)
            worksheet.merge_range(f"B{contact_start + 1 + i}:C{contact_start + 1 + i}", contact_values[i], cell_format)

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