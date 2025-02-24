from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class RFPPortal(CustomerPortal):
    @http.route(['/my/dashboard'], type='http', auth='user', website=True)
    def portal_dashboard(self, **kw):
        return request.render('procurement_management.rfp_dashboard_view')


    @http.route(['/my/rfps', '/my/rfps/page/<int:page>'], type='http', auth='user', website=True)
    def portal_rfps_list(self, page=1, sortby=None, search=None, search_in='all', groupby='none', **kw):
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
        search_domain.append(('status', '!=', 'closed')) # Show only closed RFPs

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
        if not rfp or rfp.status == 'closed':
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

        # Validate values to prevent negative inputs
        negative_values = []
        for line in rfp.product_line_ids:
            unit_price = float(kw.get(f'price_unit_{line.id}', 0.0))
            delivery_charge = float(kw.get(f'delivery_charge_{line.id}', 0.0))
            quantity = line.quantity  # Assuming quantity is already set in the RFP product lines
            warranty_period = float(kw.get(f'warranty_period', 0.0))  # Get warranty period from the input

            # Check for negative values
            if unit_price < 0:
                negative_values.append(f"Unit price for product {line.product_id.name} cannot be negative.")
            if delivery_charge < 0:
                negative_values.append(f"Delivery charge for product {line.product_id.name} cannot be negative.")
            if quantity < 0:
                negative_values.append(f"Quantity for product {line.product_id.name} cannot be negative.")
            if warranty_period < 0:
                negative_values.append(f"Warranty period for product {line.product_id.name} cannot be negative.")

        # If there are any negative values, return a warning and prevent submission
        if negative_values:
            return request.render('procurement_management.rfp_form_view_template', {
                'warning_messages': negative_values,
                'rfp': rfp,
            })

        # If no negative values, create the RFQ
        rfq = request.env['purchase.order'].sudo().create(rfq_values)

        # ✅ Add RFQ Lines
        for line in rfp.product_line_ids:
            unit_price = float(kw.get(f'price_unit_{line.id}', 0.0))
            delivery_charge = float(kw.get(f'delivery_charge_{line.id}', 0.0))

            subtotal = (line.quantity * unit_price) + delivery_charge  # ✅ Include Delivery Charges

            rfq_line_values = {
                'order_id': rfq.id,
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'price_unit': unit_price,
                'delivery_charge': delivery_charge,
                'price_total': subtotal,  # ✅ Ensure total price is stored correctly
            }
            request.env['purchase.order.line'].sudo().create(rfq_line_values)

        return request.redirect('/my/rfp/success')


    @http.route(['/my/rfp/success'], type='http', auth='user', website=True)
    def rfq_submission_success(self):

        return request.render('procurement_management.rfq_submit_view_template')


    @http.route(['/my/all_rfps', '/my/all_rfps/page/<int:page>'], type='http', auth='user', website=True)
    def portal_all_rfps_list(self, page=1, sortby=None, search=None, search_in='all', groupby='status', **kw):
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('RFP Name'), 'order': 'name'},
            'required_date': {'label': _('Required Date'), 'order': 'required_date'},
            'status': {'label': _('Status'), 'order': 'status'},
        }

        # Add additional filters for search
        search_list = {
            'all': {'label': _('All'), 'domain': []},  # No filter for 'All'
            'name': {'label': _('RFP Name'), 'domain': [('name', 'ilike', search)]},
            'status': {'label': _('Status'), 'domain': [('status', 'ilike', search)]},
        }

        # Get the domain based on search_in and search criteria
        search_domain = search_list.get(search_in, {'domain': []})['domain']

        if search_in == 'status' and search:
            search_domain.append(('status', '=', search))  # Exact match for status if provided

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Fetch RFPs based on the search domain
        rfp_obj = request.env['procurement_management.rfp'].sudo()
        rfp_count = rfp_obj.search_count(search_domain)
        items_per_page = 10

        # Create the pager object
        pager = portal_pager(url='/my/all_rfps', total=rfp_count, page=page, step=items_per_page)

        rfps = rfp_obj.search(search_domain, limit=items_per_page, offset=pager['offset'], order=order)

        grouped_rfps = []
        if groupby != 'none':
            grouped_rfps = [{
                'group': key,
                'rfps': list(values)
            } for key, values in groupbyelem(rfps, itemgetter(groupby))]

        return request.render('procurement_management.rfp_all_list_view_template', {
            'rfps': rfps,
            'grouped_rfps': grouped_rfps,
            'page_name': 'rfp_all_portal',
            'pager': pager,  # Pass the pager object to the template
            'prev_url': f"/my/all_rfps/page/{page - 1}" if page > 1 else None,
            'next_url': f"/my/all_rfps/page/{page + 1}" if (page * items_per_page) < rfp_count else None,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'groupby': groupby,
            'default_url': '/my/all_rfps',
        })


    @http.route('/my/all_rfps/<int:rfp_id>', auth='user', website=True)
    def portal_all_rfps_details(self, rfp_id, **kw):
        rfp = request.env['procurement_management.rfp'].sudo().browse(rfp_id)
        return request.render('procurement_management.rfps_all_form_view_template', {'rfp': rfp})