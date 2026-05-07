from odoo import fields, models, tools


class InvoiceProductCurrencyReport(models.Model):
    _name = "invoice.product.currency.report"
    _description = "Invoice Product Currency Report"
    _auto = False
    _rec_name = "product_name"

    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    product_name = fields.Char(string="Product", readonly=True)

    invoice_date = fields.Date(string="Invoice Date", readonly=True)
    due_date = fields.Date(string="Due Date", readonly=True)

    partner_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    commercial_partner_id = fields.Many2one(
        "res.partner",
        string="Commercial Entity",
        readonly=True
    )

    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    journal_id = fields.Many2one("account.journal", string="Journal", readonly=True)

    invoice_user_id = fields.Many2one("res.users", string="Salesperson", readonly=True)
    team_id = fields.Many2one("crm.team", string="Sales Team", readonly=True)

    product_categ_id = fields.Many2one(
        "product.category",
        string="Product Category",
        readonly=True
    )

    quantity = fields.Float(string="Quantity", readonly=True)

    purchase_cost = fields.Float(
        string="Purchase Cost",
        compute="_compute_purchase_cost",
        readonly=True
    )

    amount_untaxed_usd = fields.Float(string="Tax Excluded USD", readonly=True)
    amount_untaxed_srd = fields.Float(string="Tax Excluded SRD", readonly=True)

    amount_total_usd = fields.Float(string="Total USD", readonly=True)
    amount_total_srd = fields.Float(string="Total SRD", readonly=True)

    def _compute_purchase_cost(self):
        for rec in self:
            rec.purchase_cost = rec.product_id.standard_price or 0.0

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute("""
            CREATE OR REPLACE VIEW invoice_product_currency_report AS (

                SELECT
                    MIN(aml.id) as id,

                    aml.product_id as product_id,
                    MIN(COALESCE(pt.name->>'en_US', pt.name::text)) as product_name,

                    MIN(am.invoice_date) as invoice_date,
                    MIN(am.invoice_date_due) as due_date,

                    MIN(am.partner_id) as partner_id,
                    MIN(rp.commercial_partner_id) as commercial_partner_id,

                    MIN(am.currency_id) as currency_id,
                    MIN(am.company_id) as company_id,
                    MIN(am.journal_id) as journal_id,

                    MIN(am.invoice_user_id) as invoice_user_id,
                    MIN(am.team_id) as team_id,

                    MIN(pt.categ_id) as product_categ_id,

                    SUM(aml.quantity) as quantity,

                    SUM(
                        CASE
                            WHEN rc.name = 'USD'
                            THEN aml.price_subtotal
                            ELSE 0
                        END
                    ) as amount_untaxed_usd,

                    SUM(
                        CASE
                            WHEN rc.name = 'SRD'
                            THEN aml.price_subtotal
                            ELSE 0
                        END
                    ) as amount_untaxed_srd,

                    SUM(
                        CASE
                            WHEN rc.name = 'USD'
                            THEN aml.price_total
                            ELSE 0
                        END
                    ) as amount_total_usd,

                    SUM(
                        CASE
                            WHEN rc.name = 'SRD'
                            THEN aml.price_total
                            ELSE 0
                        END
                    ) as amount_total_srd

                FROM account_move_line aml

                INNER JOIN account_move am
                    ON aml.move_id = am.id

                INNER JOIN res_currency rc
                    ON am.currency_id = rc.id

                INNER JOIN product_product pp
                    ON aml.product_id = pp.id

                INNER JOIN product_template pt
                    ON pp.product_tmpl_id = pt.id

                LEFT JOIN res_partner rp
                    ON am.partner_id = rp.id

                WHERE
                    aml.product_id IS NOT NULL
                    AND am.move_type = 'out_invoice'
                    AND am.state = 'posted'

                GROUP BY
                    aml.product_id

            )
        """)