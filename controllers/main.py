import logging
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class RuniaWebsiteSale(WebsiteSale):

    @http.route(['/shop/cart'], type='http', auth='public', website=True)
    def cart(self, **post):
        order = request.website.sale_get_order()
        if order:
            _logger.warning(">>> DEBUG: cart() triggered, adding unique code to order %s", order.name)
            order.sudo()._add_unique_code_line()
        return super(RuniaWebsiteSale, self).cart(**post)

    @http.route(['/shop/payment'], type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        if order:
            _logger.warning(">>> DEBUG: shop_payment() triggered for order %s", order.name)
            order.sudo()._add_unique_code_line()
        return super(RuniaWebsiteSale, self).shop_payment(**post)

    def _get_shop_payment_values(self, order, **kwargs):
        if order:
            _logger.warning(">>> DEBUG: _get_shop_payment_values() triggered for order %s", order.name)
            order.sudo()._add_unique_code_line()
        return super(RuniaWebsiteSale, self)._get_shop_payment_values(order, **kwargs)
