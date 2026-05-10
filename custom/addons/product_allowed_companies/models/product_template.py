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

    display_list_price = fields.Char(
        string="Sales Price Display",
        compute="_compute_display_prices",
        store=False,
    )

    display_standard_price = fields.Char(
        string="Cost Display",
        compute="_compute_display_prices",
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

    @api.depends("list_price", "standard_price", "display_currency_id")
    def _compute_display_prices(self):
        for product in self:
            currency = product.display_currency_id or self.env.company.currency_id
            currency_name = currency.name or ""

            product.display_list_price = f"{product.list_price:.2f} {currency_name}"
            product.display_standard_price = f"{product.standard_price:.2f} {currency_name}"


class ProductProduct(models.Model):
    _inherit = "product.product"

    allowed_company_ids = fields.Many2many(
        related="product_tmpl_id.allowed_company_ids",
        string="Allowed Companies",
        readonly=True,
    )

    display_currency_id = fields.Many2one(
        related="product_tmpl_id.display_currency_id",
        string="Display Currency",
        readonly=True,
    )

    display_list_price = fields.Char(
        related="product_tmpl_id.display_list_price",
        string="Sales Price Display",
        readonly=True,
    )

    display_standard_price = fields.Char(
        related="product_tmpl_id.display_standard_price",
        string="Cost Display",
        readonly=True,
    )