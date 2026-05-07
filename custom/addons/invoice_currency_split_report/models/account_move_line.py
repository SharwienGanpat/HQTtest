from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    amount_usd = fields.Float(
        string="USD Amount",
        compute="_compute_currency_split_amounts",
        store=True,
    )

    amount_srd = fields.Float(
        string="SRD Amount",
        compute="_compute_currency_split_amounts",
        store=True,
    )

    @api.depends(
        "price_subtotal",
        "display_type",
        "move_id.currency_id",
        "move_id.move_type",
    )
    def _compute_currency_split_amounts(self):
        for line in self:
            line.amount_usd = 0.0
            line.amount_srd = 0.0

            if line.display_type in ("line_section", "line_note"):
                continue

            if line.move_id.move_type not in ("out_invoice", "out_refund"):
                continue

            amount = line.price_subtotal or 0.0

            if line.move_id.move_type == "out_refund":
                amount = -amount

            currency_name = line.move_id.currency_id.name

            if currency_name == "USD":
                line.amount_usd = amount
            elif currency_name == "SRD":
                line.amount_srd = amount