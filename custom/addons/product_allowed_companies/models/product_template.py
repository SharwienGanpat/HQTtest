from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allowed_company_ids = fields.Many2many(
        "res.company",
        "product_template_allowed_company_rel",
        "product_tmpl_id",
        "company_id",
        string="Allowed Companies",
        help="If empty, the product is visible to all companies. "
             "If set, the product is visible only to the selected companies.",
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    allowed_company_ids = fields.Many2many(
        related="product_tmpl_id.allowed_company_ids",
        string="Allowed Companies",
        readonly=True,
    )