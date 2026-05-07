from odoo import fields, models
from odoo.exceptions import UserError


class InvoiceProductReportWizard(models.TransientModel):
    _name = "invoice.product.report.wizard"
    _description = "Invoice Product Report Wizard"

    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)

    def action_generate_report(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise UserError("From Date cannot be later than To Date.")

        Result = self.env["invoice.product.currency.report.result"]

        # Clear only this user's temporary report lines
        Result.search([("create_uid", "=", self.env.user.id)]).unlink()

        self.env.cr.execute("""
            SELECT
                aml.product_id AS product_id,

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
            JOIN account_move am ON aml.move_id = am.id
            JOIN res_currency rc ON am.currency_id = rc.id

            WHERE aml.product_id IS NOT NULL
              AND am.move_type IN ('out_invoice', 'out_refund')
              AND am.state = 'posted'
              AND am.invoice_date >= %s
              AND am.invoice_date <= %s
              AND COALESCE(aml.display_type, '') NOT IN ('line_section', 'line_note')

            GROUP BY aml.product_id
        """, (self.date_from, self.date_to))

        rows = self.env.cr.dictfetchall()

        for row in rows:
            product = self.env["product.product"].browse(row["product_id"])

            Result.create({
                "product_id": product.id,
                "product_name": product.display_name,
                "quantity": row["quantity"] or 0.0,
                "purchase_cost": product.standard_price or 0.0,
                "amount_untaxed_usd": row["amount_untaxed_usd"] or 0.0,
                "amount_untaxed_srd": row["amount_untaxed_srd"] or 0.0,
                "amount_total_usd": row["amount_total_usd"] or 0.0,
                "amount_total_srd": row["amount_total_srd"] or 0.0,
                "date_from": self.date_from,
                "date_to": self.date_to,
            })

        return {
            "type": "ir.actions.act_window",
            "name": "Invoice Product Currency Report",
            "res_model": "invoice.product.currency.report.result",
            "view_mode": "list",
            "target": "current",
            "domain": [("create_uid", "=", self.env.user.id)],
        }


class InvoiceProductCurrencyReportResult(models.TransientModel):
    _name = "invoice.product.currency.report.result"
    _description = "Invoice Product Currency Report Result"
    _rec_name = "product_name"
    _order = "product_name"

    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    product_name = fields.Char(string="Product", readonly=True)

    quantity = fields.Float(string="Quantity", readonly=True)
    purchase_cost = fields.Float(string="Purchase Cost", readonly=True)

    amount_untaxed_usd = fields.Float(string="Tax Excluded USD", readonly=True)
    amount_untaxed_srd = fields.Float(string="Tax Excluded SRD", readonly=True)

    amount_total_usd = fields.Float(string="Total USD", readonly=True)
    amount_total_srd = fields.Float(string="Total SRD", readonly=True)

    date_from = fields.Date(string="From Date", readonly=True)
    date_to = fields.Date(string="To Date", readonly=True)