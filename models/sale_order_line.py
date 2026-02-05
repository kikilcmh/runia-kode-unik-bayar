from odoo import models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _show_in_cart(self):
        self.ensure_one()
        product_kode_unik = self.env.ref('runia_kode_unik_bayar.product_product_kode_unik', raise_if_not_found=False)
        if product_kode_unik and self.product_id == product_kode_unik:
            return False
        return super(SaleOrderLine, self)._show_in_cart()

    def _compute_price_unit(self):
        # Prevent Odoo from resetting the unique code price to 0 (product price)
        product_kode_unik = self.env.ref('runia_kode_unik_bayar.product_product_kode_unik', raise_if_not_found=False)
        unique_lines = self.filtered(lambda l: l.product_id == product_kode_unik)
        super(SaleOrderLine, self - unique_lines)._compute_price_unit()
