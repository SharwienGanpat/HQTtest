/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);

        // Automatically mark invoice = true
        this.to_invoice = true;
    },
});