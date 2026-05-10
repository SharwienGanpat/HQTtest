from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id", "product_uom_qty", "product_uom", "order_id.currency_id")
    def _onchange_product_price_currency_id(self):
        for line in self:
            product = line.product_id
            order = line.order_id

            if not product or not order:
                continue

            source_currency = product.product_tmpl_id.product_price_currency_id
            target_currency = order.currency_id

            if not source_currency or not target_currency:
                continue

            # Use the raw product sales price from the template
            price = product.product_tmpl_id.list_price

            if source_currency.id == target_currency.id:
                line.price_unit = price
            else:
                line.price_unit = source_currency._convert(
                    price,
                    target_currency,
                    order.company_id,
                    order.date_order or fields.Date.context_today(line),
                )