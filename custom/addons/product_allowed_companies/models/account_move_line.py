from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_price_currency_custom(self):
        for line in self:
            product = line.product_id
            move = line.move_id

            if not product or not move:
                continue

            # Only customer invoices / credit notes
            if move.move_type not in ("out_invoice", "out_refund"):
                continue

            source_currency = product.product_price_currency_id
            target_currency = move.currency_id

            if not source_currency or not target_currency:
                continue

            price = product.lst_price

            # Convert only if currencies differ
            if source_currency != target_currency:
                price = source_currency._convert(
                    price,
                    target_currency,
                    move.company_id,
                    move.invoice_date or fields.Date.context_today(line),
                )

            line.price_unit = price