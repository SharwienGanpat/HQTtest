{
    "name": "Product Allowed Companies",
    "version": "18.0.1.0.0",
    "category": "Product",
    "summary": "Restrict product visibility to selected companies",
    "depends": ["product", "sale", "account"],
    "data": [
        "security/product_security.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}