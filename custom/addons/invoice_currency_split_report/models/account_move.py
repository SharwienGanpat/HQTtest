from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_untaxed_usd = fields.Float(
        string="Tax Excluded USD",
        compute="_compute_currency_split_totals",
        store=True,
    )

    amount_untaxed_srd = fields.Float(
        string="Tax Excluded SRD",
        compute="_compute_currency_split_totals",
        store=True,
    )

    amount_total_usd = fields.Float(
        string="Total USD",
        compute="_compute_currency_split_totals",
        store=True,
    )

    amount_total_srd = fields.Float(
        string="Total SRD",
        compute="_compute_currency_split_totals",
        store=True,
    )

    @api.depends("currency_id", "amount_untaxed", "amount_total", "move_type")
    def _compute_currency_split_totals(self):
        for move in self:
            move.amount_untaxed_usd = 0.0
            move.amount_untaxed_srd = 0.0
            move.amount_total_usd = 0.0
            move.amount_total_srd = 0.0

            if move.move_type not in ("out_invoice", "out_refund"):
                continue

            sign = -1 if move.move_type == "out_refund" else 1

            if move.currency_id.name == "USD":
                move.amount_untaxed_usd = sign * move.amount_untaxed
                move.amount_total_usd = sign * move.amount_total

            elif move.currency_id.name == "SRD":
                move.amount_untaxed_srd = sign * move.amount_untaxed
                move.amount_total_srd = sign * move.amount_total