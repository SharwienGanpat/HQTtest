from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    amount_usd = fields.Float(
        string="Total USD",
        readonly=True
    )

    amount_srd = fields.Float(
        string="Total SRD",
        readonly=True
    )

    def _select(self):
        select_str = super()._select()

        # Replace IDs with your actual currencies
        usd_currency_id = 2
        srd_currency_id = 124

        select_str += f"""
            ,
            CASE
                WHEN move.currency_id = {usd_currency_id}
                THEN move.amount_total_in_currency
                ELSE 0
            END as amount_usd,

            CASE
                WHEN move.currency_id = {srd_currency_id}
                THEN move.amount_total_in_currency
                ELSE 0
            END as amount_srd
        """

        return select_str