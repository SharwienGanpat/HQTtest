from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id", "move_id.currency_id", "quantity")
    def _onchange_product_price_currency_custom(self):
        for line in self:
            product = line.product_id
            move = line.move_id

            if not product or not move:
                continue

            if move.move_type not in ("out_invoice", "out_refund"):
                continue

            source_currency = product.product_price_currency_id
            target_currency = move.currency_id

            if not source_currency or not target_currency:
                continue

            price = product.lst_price

            # Same currency: use product price directly
            if source_currency.id == target_currency.id:
                line.price_unit = price
                continue

            # Different currency: convert
            line.price_unit = source_currency._convert(
                price,
                target_currency,
                move.company_id,
                move.invoice_date or fields.Date.context_today(line),
            )