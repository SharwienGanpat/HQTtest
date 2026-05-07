from odoo import fields, models


class InvoiceProductReportWizard(models.TransientModel):
    _name = "invoice.product.report.wizard"
    _description = "Invoice Product Report Wizard"

    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)

    def action_open_report(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Invoice Product Currency Report",
            "res_model": "invoice.product.currency.report",
            "view_mode": "list",
            "target": "current",
            "context": {
                "date_from": self.date_from.strftime("%Y-%m-%d"),
                "date_to": self.date_to.strftime("%Y-%m-%d"),
            },
        }