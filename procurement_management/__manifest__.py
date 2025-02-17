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
    'depends': ['base', 'purchase', 'web', 'mail', 'website', 'portal', 'account', 'contacts'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/procurement_security.xml',
        'security/rule_rfp.xml',
        'security/ir.model.access.csv',
        'reports/rfp_qweb_template.xml',
        'views/rfp_report_views.xml',
        'views/all_email_templates.xml',
        'views/email_template_supplier_rejection.xml',
        'views/approver.xml',
        'views/reviewer.xml',
        'views/rfp_views.xml',
        'views/inherited_purchase_order_views.xml',
        'views/menus.xml',
        'views/portal_rfp_views.xml',
        'views/portal_vendor_rfp_templates.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

