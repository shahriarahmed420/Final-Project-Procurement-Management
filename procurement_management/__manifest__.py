# -*- coding: utf-8 -*-
{
    'name': "Procurement_Management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'web', 'website', 'portal', 'account', 'contacts'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/procurement_security.xml',
        'security/rule_rfp.xml',
        'security/ir.model.access.csv',
        'reports/rfp_qweb_template.xml',
        'views/rfp_report_views.xml',
        'views/approver_views.xml',
        'views/reviewer_views.xml',
        'views/rfp_views.xml',
        'views/dashboard_views.xml',
        'views/inherited_purchase_order_views.xml',
        'views/inherited_bank_views.xml',
        'views/inherited_res_partner_views.xml',
        'views/menus.xml',
        'views/portal_rfp_templates.xml',
        'views/portal_vendor_rfp_templates.xml',
        'views/supplier_registration_templates.xml',
        'demo/registration_form_demo.xml',
        'demo/rfp_demo.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'procurement_management/static/src/js/chart_renderer.js',
            'procurement_management/static/src/css/dashboard_css.css',
            'procurement_management/static/src/js/procurement_dashboard.js',
            'procurement_management/static/src/xml/chart_renderer.xml',
            'procurement_management/static/src/xml/procurement_dashboard_templates.xml',
        ],
    },
}

