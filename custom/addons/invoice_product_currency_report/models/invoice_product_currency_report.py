from odoo import fields, models, tools


class InvoiceProductCurrencyReport(models.Model):
    _name = "invoice.product.currency.report"
    _description = "Invoice Product Currency Report"
    _auto = False
    _order = "product_name"

    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    product_name = fields.Char(string="Product", readonly=True)
    product_categ_id = fields.Many2one("product.category", string="Product Category", readonly=True)

    invoice_date = fields.Date(string="Invoice Date", readonly=True)
    due_date = fields.Date(string="Due Date", readonly=True)

    partner_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    commercial_partner_id = fields.Many2one("res.partner", string="Commercial Entity", readonly=True)

    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    journal_id = fields.Many2one("account.journal", string="Journal", readonly=True)

    invoice_user_id = fields.Many2one("res.users", string="Salesperson", readonly=True)
    team_id = fields.Many2one("crm.team", string="Sales Team", readonly=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancel", "Cancelled"),
        ],
        string="Invoice Status",
        readonly=True,
    )

    payment_state = fields.Selection(
        [
            ("not_paid", "Not Paid"),
            ("in_payment", "In Payment"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
            ("reversed", "Reversed"),
            ("blocked", "Blocked"),
            ("invoicing_legacy", "Invoicing App Legacy"),
        ],
        string="Payment Status",
        readonly=True,
    )

    quantity = fields.Float(string="Quantity", readonly=True)
    purchase_cost = fields.Float(
        string="Purchase Cost",
        compute="_compute_purchase_cost",
        readonly=True,
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
                    MIN(aml.id) AS id,

                    aml.product_id AS product_id,
                    COALESCE(pt.name->>'en_US', pt.name::text) AS product_name,
                    pt.categ_id AS product_categ_id,

                    SUM(
                        CASE
                            WHEN am.move_type = 'out_refund'
                            THEN -aml.quantity
                            ELSE aml.quantity
                        END
                    ) AS quantity,

                    SUM(
                        CASE
                            WHEN rc.name = 'USD' AND am.move_type = 'out_refund'
                            THEN -aml.price_subtotal
                            WHEN rc.name = 'USD'
                            THEN aml.price_subtotal
                            ELSE 0
                        END
                    ) AS amount_untaxed_usd,

                    SUM(
                        CASE
                            WHEN rc.name = 'SRD' AND am.move_type = 'out_refund'
                            THEN -aml.price_subtotal
                            WHEN rc.name = 'SRD'
                            THEN aml.price_subtotal
                            ELSE 0
                        END
                    ) AS amount_untaxed_srd,

                    SUM(
                        CASE
                            WHEN rc.name = 'USD' AND am.move_type = 'out_refund'
                            THEN -aml.price_total
                            WHEN rc.name = 'USD'
                            THEN aml.price_total
                            ELSE 0
                        END
                    ) AS amount_total_usd,

                    SUM(
                        CASE
                            WHEN rc.name = 'SRD' AND am.move_type = 'out_refund'
                            THEN -aml.price_total
                            WHEN rc.name = 'SRD'
                            THEN aml.price_total
                            ELSE 0
                        END
                    ) AS amount_total_srd

                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                JOIN res_currency rc ON rc.id = am.currency_id
                JOIN product_product pp ON pp.id = aml.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id

                WHERE am.move_type IN ('out_invoice', 'out_refund')
                  AND aml.product_id IS NOT NULL
                  AND COALESCE(aml.display_type, '') NOT IN ('line_section', 'line_note')

                GROUP BY
                    aml.product_id,
                    COALESCE(pt.name->>'en_US', pt.name::text),
                    pt.categ_id,

            )
        """)