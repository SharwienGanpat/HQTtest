from odoo import api, fields, models


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

    display_currency_id = fields.Many2one(
        "res.currency",
        string="Display Currency",
        compute="_compute_display_currency_id",
        store=False,
    )

    @api.depends("company_id", "allowed_company_ids")
    def _compute_display_currency_id(self):
        usd = self.env.ref("base.USD", raise_if_not_found=False)

        for product in self:
            if product.company_id:
                product.display_currency_id = product.company_id.currency_id
            elif product.allowed_company_ids:
                currencies = product.allowed_company_ids.mapped("currency_id")
                if len(currencies) == 1:
                    product.display_currency_id = currencies[0]
                elif usd:
                    product.display_currency_id = usd
                else:
                    product.display_currency_id = self.env.company.currency_id
            elif usd:
                product.display_currency_id = usd
            else:
                product.display_currency_id = self.env.company.currency_id


class ProductProduct(models.Model):
    _inherit = "product.product"

    allowed_company_ids = fields.Many2many(
        related="product_tmpl_id.allowed_company_ids",
        string="Allowed Companies",
        readonly=True,
    )