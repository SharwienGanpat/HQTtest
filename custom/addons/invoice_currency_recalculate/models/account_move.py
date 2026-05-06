from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("currency_id")
    def _onchange_currency_id_recalculate_invoice_lines(self):
        """
        When invoice currency changes:
        Convert existing invoice line prices to the new currency.
        Example:
        USD 8.26 -> SRD 318.01 (if rate = 38.5)
        """
        for move in self:

            # Only customer/vendor invoices
            if move.move_type not in (
                'out_invoice',
                'out_refund',
                'in_invoice',
                'in_refund'
            ):
                continue

            # No lines yet
            if not move.invoice_line_ids:
                continue

            # Currency before user changed it
            old_currency = move._origin.currency_id

            # Newly selected currency
            new_currency = move.currency_id

            if not old_currency or not new_currency:
                continue

            # Same currency → nothing to do
            if old_currency == new_currency:
                continue

            # Use invoice date for rate lookup
            date = move.invoice_date or fields.Date.context_today(move)

            for line in move.invoice_line_ids:

                # Skip notes/sections
                if line.display_type:
                    continue

                # Skip empty lines
                if not line.product_id:
                    continue

                old_price = line.price_unit or 0.0

                # Convert old price → new currency
                new_price = old_currency._convert(
                    old_price,
                    new_currency,
                    move.company_id,
                    date,
                )

                # Update invoice line price
                line.price_unit = new_price