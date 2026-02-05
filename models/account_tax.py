from odoo import models, fields, api

class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_unique_code_tax = fields.Boolean(string="Is Unique Code Tax")

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, fixed_multiplicator=1):
        """ Allow dynamic adjustment of tax amount if needed, though usually fixed on line is easier """
        return super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner, fixed_multiplicator)
