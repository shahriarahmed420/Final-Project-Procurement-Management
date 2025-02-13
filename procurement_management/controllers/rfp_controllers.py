from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class RFPPortal(CustomerPortal):

    @http.route(['/my/rfps', '/my/rfps/page/<int:page>'], type='http', auth='user', website=True)
    def portal_rfps_list(self, page=1, sortby=None, search=None, search_in='all', groupby='none', **kw):
        """ Displays the list of approved RFPs in the portal. """

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('RFP Name'), 'order': 'name'},
            'required_date': {'label': _('Required Date'), 'order': 'required_date'},
        }

        search_list = {
            'all': {'label': _('All'), 'domain': []},
            'name': {'label': _('RFP Name'), 'domain': [('name', 'ilike', search)]},
        }

        search_domain = search_list.get(search_in, {'domain': []})['domain']
        search_domain.append(('status', '=', 'approved'))  # Show only approved RFPs

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        rfp_obj = request.env['procurement_management.rfp']
        rfp_count = rfp_obj.search_count(search_domain)
        items_per_page = 5
        pager = portal_pager(url='/my/rfps', total=rfp_count, page=page, step=items_per_page)

        rfps = rfp_obj.search(search_domain, limit=items_per_page, offset=pager['offset'], order=order)

        return request.render('procurement_management.rfp_list_view_template', {
            'rfps': rfps,
            'page_name': 'rfp_portal',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'default_url': '/my/rfps',
        })

    @http.route('/my/rfp/<int:rfp_id>', auth='user', website=True)
    def portal_rfp_details(self, rfp_id, **kw):
        """ Displays full details of a selected RFP. """
        rfp = request.env['procurement_management.rfp'].sudo().browse(rfp_id)
        return request.render('procurement_management.rfp_form_view_template', {'rfp': rfp})

    @http.route(['/my/rfp/<int:rfp_id>/submit_rfq'], type='http', auth='user', website=True)
    def portal_submit_rfq(self, rfp_id, **kw):
        """ Handles RFQ submission for an RFP. Allows multiple RFQs per vendor and ensures proper Buyer & Vendor names. """

        rfp = request.env['procurement_management.rfp'].sudo().browse(rfp_id)
        if not rfp:
            return request.redirect('/my/rfps')

        # ✅ Ensure the Partner ID is properly linked (Vendor)
        partner = request.env.user.partner_id
        if not partner:
            return request.redirect('/my/rfps')

        # ✅ Assign Buyer (Procurement Responsible User - The one who created the RFP)
        buyer = rfp.create_uid  # The user who created the RFP

        # ✅ Allow Multiple RFQs from the Same Vendor (DO NOT CHECK EXISTING RFQ)
        rfq_values = {
            'rfp_id': rfp.id,
            'partner_id': partner.id,  # ✅ Vendor (Supplier submitting RFQ)
            'user_id': buyer.id,  # ✅ Buyer (Procurement User who created the RFP)
            'expected_delivery_date': kw.get('expected_delivery_date'),
            'terms_conditions': kw.get('terms_conditions'),
            'warranty_period': kw.get('warranty_period'),
            'state': 'draft',  # ✅ Ensure RFQ is created in Draft state
        }
        rfq = request.env['purchase.order'].sudo().create(rfq_values)

        # ✅ Add RFQ Lines
        for line in rfp.product_line_ids:
            rfq_line_values = {
                'order_id': rfq.id,
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'price_unit': float(kw.get(f'price_unit_{line.id}', 0.0)),
                'delivery_charge': float(kw.get(f'delivery_charge_{line.id}', 0.0)),
            }
            request.env['purchase.order.line'].sudo().create(rfq_line_values)

        return request.redirect(f'/my/rfp/{rfp.id}')