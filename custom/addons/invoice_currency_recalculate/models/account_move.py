from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    previous_currency_id = fields.Many2one(
        "res.currency",
        string="Previous Currency",
        copy=False,
    )

    @api.onchange("currency_id")
    def _onchange_currency_id_recalculate_prices(self):
        for move in self:
            new_currency = move.currency_id

            if not new_currency:
                continue

            old_currency = (
                move.previous_currency_id
                or move._origin.currency_id
                or move.company_id.currency_id
            )

            # Important: prevents multiplying again when selecting same currency
            if old_currency == new_currency:
                move.previous_currency_id = new_currency
                continue

            date = move.invoice_date or fields.Date.context_today(move)

            for line in move.invoice_line_ids:
                if line.display_type in ("line_section", "line_note"):
                    continue

                new_price = old_currency._convert(
                    line.price_unit or 0.0,
                    new_currency,
                    move.company_id,
                    date,
                )

                line.price_unit = new_currency.round(new_price)

            move.previous_currency_id = new_currency