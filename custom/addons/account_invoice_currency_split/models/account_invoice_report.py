from odoo import fields, models
from odoo.tools import SQL


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
        base_select = super()._select()

        # Replace with your real currency IDs
        usd_currency_id = 1
        srd_currency_id = 140

        return SQL(
            "%s, "
            "CASE "
            "WHEN move.currency_id = %s "
            "THEN move.amount_total "
            "ELSE 0 "
            "END as amount_usd, "

            "CASE "
            "WHEN move.currency_id = %s "
            "THEN move.amount_total "
            "ELSE 0 "
            "END as amount_srd",
            base_select,
            usd_currency_id,
            srd_currency_id,
        )