import logging
from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_unique_code = fields.Monetary(string='Amount Kode Unik', compute='_compute_amounts_unique_code')
    amount_untaxed_without_unique_code = fields.Monetary(string='Untaxed Amount without Unique Code', compute='_compute_amounts_unique_code')

    @api.depends('order_line.price_total', 'order_line.price_subtotal', 'order_line.product_id', 'amount_untaxed')
    def _compute_amounts_unique_code(self):
        _logger = logging.getLogger(__name__)
        product_kode_unik = self.env.ref('runia_kode_unik_bayar.product_product_kode_unik', raise_if_not_found=False)
        for order in self:
            unique_lines = order.order_line.filtered(lambda l: l.product_id == product_kode_unik)
            amt_unique = sum(unique_lines.mapped('price_total'))
            _logger.warning(">>> DEBUG: _compute_amounts_unique_code for %s: lines=%s, amt=%s", order.name, len(unique_lines), amt_unique)
            order.amount_unique_code = amt_unique
            # amount_untaxed INCLUDES all lines. We want the subtotal EXCLUDING the unique code line.
            order.amount_untaxed_without_unique_code = order.amount_untaxed - amt_unique

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals(self):
        """ Override to inject Kode Unik into the tax totals JSON for standard display """
        super(SaleOrder, self)._compute_tax_totals()
        for order in self:
            if not order.amount_unique_code or not order.tax_totals:
                continue
            
            # Extract current totals
            totals = order.tax_totals
            
            # 1. Adjust the Subtotal (Untaxed) to EXCLUDE Kode Unik
            if 'subtotals' in totals:
                for sub in totals['subtotals']:
                    if sub.get('name') == 'Untaxed Amount':
                        sub['amount'] -= order.amount_unique_code
                        sub['formatted_amount'] = self.env['ir.qweb.field.monetary'].value_to_html(sub['amount'], {'display_currency': order.currency_id})

            # 2. Add Kode Unik as a dedicated "Tax Group" row
            unique_group = {
                'tax_group_name': 'Kode Unik',
                'tax_group_amount': order.amount_unique_code,
                'tax_group_id': self.env.ref('runia_kode_unik_bayar.tax_group_kode_unik').id,
                'formatted_tax_group_amount': self.env['ir.qweb.field.monetary'].value_to_html(order.amount_unique_code, {'display_currency': order.currency_id}),
            }
            
            # Inject into groups_by_subtotal
            if 'groups_by_subtotal' not in totals:
                totals['groups_by_subtotal'] = {}
            
            # Find the subtotal key (usually "Untaxed Amount")
            subtotal_key = 'Untaxed Amount'
            if 'subtotals' in totals and totals['subtotals']:
                subtotal_key = totals['subtotals'][0].get('name', 'Untaxed Amount')
            
            if subtotal_key not in totals['groups_by_subtotal']:
                totals['groups_by_subtotal'][subtotal_key] = []
            
            totals['groups_by_subtotal'][subtotal_key].append(unique_group)
            
            # Re-assign to trigger update
            order.tax_totals = totals

    def action_confirm(self):
        self._add_unique_code_line()
        return super(SaleOrder, self).action_confirm()

    def _add_unique_code_line(self):
        _logger = logging.getLogger(__name__)
        for order in self:
            _logger.warning(">>> DEBUG: _add_unique_code_line called for order %s", order.name)
            
            # 1. Find product
            product_kode_unik = self.env.ref('runia_kode_unik_bayar.product_product_kode_unik', raise_if_not_found=False)
            if not product_kode_unik:
                _logger.error(">>> ERROR: product_product_kode_unik NOT FOUND!")
                continue

            # 2. Check for existing line
            existing_line = order.order_line.filtered(lambda l: l.product_id == product_kode_unik)
            if existing_line:
                _logger.warning(">>> DEBUG: line already exists for order %s (Price: %s)", order.name, existing_line[0].price_unit)
                if any(l.price_unit == 0 for l in existing_line):
                    _logger.warning(">>> DEBUG: Existing line has 0 price, updating...")
                    unique_code = self._get_next_unique_code(order.company_id)
                    existing_line.write({'price_unit': unique_code})
                else:
                    continue
            else:
                # 3. Get next code
                unique_code = self._get_next_unique_code(order.company_id)
                _logger.warning(">>> DEBUG: Unique Code generated: %s", unique_code)
                if unique_code == 0:
                    continue

                # 4. Create line
                _logger.warning(">>> DEBUG: Creating line for order %s with price %s", order.name, unique_code)
                self.env['sale.order.line'].create({
                    'product_id': product_kode_unik.id,
                    'price_unit': unique_code,
                    'product_uom_qty': 1,
                    'order_id': order.id,
                    'name': 'Kode Unik Pembayaran',
                    'tax_id': [(5, 0, 0)], # No taxes on the unique code itself
                    'sequence': 999, # Ensure it's at the bottom
                })
            
            # 5. Force recompute
            order.invalidate_recordset(['amount_untaxed', 'amount_tax', 'amount_total', 'amount_unique_code'])
            # Odoo 17 recompute is usually automatic, but we can trigger it
            if hasattr(order, '_compute_amounts'):
                order._compute_amounts()

    @api.model
    def _get_next_unique_code(self, company=None):
        if not company:
            company = self.env.company
        limit = company.unique_code_limit or 500
        
        next_code = company.last_code + 1
        if next_code > limit:
            next_code = 1
            
        company.write({'last_code': next_code})
        return next_code
