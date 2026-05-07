{
    'name': 'POS Auto Invoice',
    'version': '18.0.1.0.0',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_auto_invoice/static/src/js/auto_invoice.js',
        ],
    },
    'installable': True,
}