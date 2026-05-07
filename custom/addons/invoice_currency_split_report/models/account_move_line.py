from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_name_export = fields.Char(
        string="Product",
        compute="_compute_product_name_export",
        store=True,
    )

    invoice_date_due = fields.Date(
        string="Due Date",
        related="move_id.invoice_date_due",
        store=True,
    )

    invoice_payment_state = fields.Selection(
        string="Status",
        related="move_id.payment_state",
        store=True,
    )

    amount_untaxed_usd = fields.Float(
        string="Tax Excluded USD",
        compute="_compute_currency_split_amounts",
        store=True,
    )

    amount_untaxed_srd = fields.Float(
        string="Tax Excluded SRD",
        compute="_compute_currency_split_amounts",
        store=True,
    )

    amount_total_usd = fields.Float(
        string="Total USD",
        compute="_compute_currency_split_amounts",
        store=True,
    )

    amount_total_srd = fields.Float(
        string="Total SRD",
        compute="_compute_currency_split_amounts",
        store=True,
    )

    @api.depends("product_id")
    def _compute_product_name_export(self):
        for line in self:
            line.product_name_export = line.product_id.display_name or ""

    @api.depends(
        "price_subtotal",
        "price_total",
        "display_type",
        "move_id.currency_id",
        "move_id.move_type",
    )
    def _compute_currency_split_amounts(self):
        for line in self:
            line.amount_untaxed_usd = 0.0
            line.amount_untaxed_srd = 0.0
            line.amount_total_usd = 0.0
            line.amount_total_srd = 0.0

            if line.display_type in ("line_section", "line_note"):
                continue

            if line.move_id.move_type not in ("out_invoice", "out_refund"):
                continue

            sign = -1 if line.move_id.move_type == "out_refund" else 1

            subtotal = sign * (line.price_subtotal or 0.0)
            total = sign * (line.price_total or 0.0)

            currency_name = line.move_id.currency_id.name

            if currency_name == "USD":
                line.amount_untaxed_usd = subtotal
                line.amount_total_usd = total

            elif currency_name == "SRD":
                line.amount_untaxed_srd = subtotal
                line.amount_total_srd = total