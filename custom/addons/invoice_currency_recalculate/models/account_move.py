from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    previous_currency_id = fields.Many2one(
        "res.currency",
        string="Previous Currency"
    )

    def action_recalculate_currency_prices(self):
        for move in self:
            old_currency = move.company_id.currency_id
            new_currency = move.currency_id

            if not old_currency or not new_currency:
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