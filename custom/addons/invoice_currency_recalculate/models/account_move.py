from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    previous_currency_id = fields.Many2one(
        "res.currency",
        string="Previous Currency"
    )

    @api.onchange("invoice_line_ids")
    def _onchange_invoice_line_ids_set_previous_currency(self):
        for move in self:
            if move.currency_id and not move.previous_currency_id:
                move.previous_currency_id = move.currency_id

    @api.onchange("currency_id")
    def _onchange_currency_id_recalculate_invoice_lines(self):
        for move in self:
            new_currency = move.currency_id
            old_currency = move.previous_currency_id or move._origin.currency_id

            if not old_currency or not new_currency:
                move.previous_currency_id = new_currency
                continue

            if old_currency == new_currency:
                move.previous_currency_id = new_currency
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

            move.previous_currency_id = new_currency