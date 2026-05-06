from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("currency_id")
    def _onchange_currency_id_recalculate_invoice_lines(self):
        for move in self:
            if not move.invoice_line_ids:
                continue

            new_currency = move.currency_id

            # Try to get old currency.
            # If this is a new unsaved invoice, _origin may be empty.
            old_currency = move._origin.currency_id or move.company_id.currency_id

            if not old_currency or not new_currency:
                continue

            if old_currency == new_currency:
                continue

            date = move.invoice_date or fields.Date.context_today(move)

            for line in move.invoice_line_ids:
                if line.display_type:
                    continue

                old_price = line.price_unit or 0.0

                new_price = old_currency._convert(
                    old_price,
                    new_currency,
                    move.company_id,
                    date,
                )

                line.price_unit = new_currency.round(new_price)