from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class VendorRFPPortal(CustomerPortal):

    @http.route(['/my/vendor_rfps', '/my/vendor_rfps/page/<int:page>'], type='http', auth='user', website=True)
    def portal_vendor_rfps(self, page=1, sortby=None, **kw):
        """ Display a paginated list of accepted RFQs (turned into Purchase Orders) for the logged-in supplier """

        partner_id = request.env.user.partner_id.id
        search_domain = [('partner_id', '=', partner_id), ('state', '=', 'purchase')]

        # Sorting options
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date_order desc'},
            'rfp': {'label': _('RFP ID'), 'order': 'rfp_id'},
            'amount': {'label': _('Total Amount'), 'order': 'amount_total desc'},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Pagination Logic
        rfq_obj = request.env['purchase.order'].sudo()
        rfq_count = rfq_obj.search_count(search_domain)
        items_per_page = 5  # Number of items per page

        pager = portal_pager(
            url='/my/vendor_rfps',
            total=rfq_count,
            page=page,
            step=items_per_page
        )

        total_pages = max(1, (rfq_count + items_per_page - 1) // items_per_page)  # Ensure at least 1 page
        prev_page = max(1, page - 1) if page > 1 else None
        next_page = min(total_pages, page + 1) if page < total_pages else None

        rfqs = rfq_obj.search(search_domain, limit=items_per_page, offset=pager['offset'], order=order)


        return request.render('procurement_management.vendor_rfp_list_template', {
            'rfqs': rfqs,
            'page_name': 'vendor_rfp_portal',
            'pager': pager,
            'prev_page': prev_page,
            'next_page': next_page,
            'total_pages': total_pages,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'default_url': '/my/vendor_rfps',
        })

    @http.route('/my/vendor_rfp/<int:rfq_id>', auth='user', website=True)
    def portal_vendor_rfp_details(self, rfq_id, **kw):
        rfq = request.env['purchase.order'].sudo().browse(rfq_id)
        return request.render('procurement_management.vendor_rfp_form_template', {'rfq': rfq})
