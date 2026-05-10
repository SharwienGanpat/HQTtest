from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _set_custom_product_currency_prices(self):
        for order in self:
            target_currency = order.currency_id
            if not target_currency:
                continue

            for line in order.order_line:
                product = line.product_id
                if not product:
                    continue

                template = product.product_tmpl_id
                source_currency = template.product_price_currency_id

                if not source_currency:
                    continue

                price = template.list_price

                if source_currency.id != target_currency.id:
                    price = source_currency._convert(
                        price,
                        target_currency,
                        order.company_id,
                        order.date_order or fields.Date.context_today(order),
                    )

                line.price_unit = price

    @api.onchange("pricelist_id", "currency_id", "date_order")
    def _onchange_pricelist_currency_custom_product_price(self):
        self._set_custom_product_currency_prices()