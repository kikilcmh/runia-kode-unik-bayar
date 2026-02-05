import logging
from odoo import models, api, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_unique_code = fields.Monetary(string='Amount Kode Unik', compute='_compute_amounts_unique_code')

    @api.depends('invoice_line_ids.price_total', 'invoice_line_ids.product_id')
    def _compute_amounts_unique_code(self):
        product_kode_unik = self.env.ref('runia_kode_unik_bayar.product_product_kode_unik', raise_if_not_found=False)
        for move in self:
            unique_lines = move.invoice_line_ids.filtered(lambda l: l.product_id == product_kode_unik)
            move.amount_unique_code = sum(unique_lines.mapped('price_total'))

    @api.depends('invoice_line_ids.tax_ids', 'invoice_line_ids.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals(self):
        """ Override to inject Kode Unik into the tax totals JSON for standard display """
        super(AccountMove, self)._compute_tax_totals()
        for move in self:
            if not move.amount_unique_code or not move.tax_totals:
                continue
            
            # Extract current totals
            totals = move.tax_totals
            
            # 1. Adjust the Subtotal (Untaxed) to EXCLUDE Kode Unik
            if 'subtotals' in totals:
                for sub in totals['subtotals']:
                    if sub.get('name') == 'Untaxed Amount':
                        sub['amount'] -= move.amount_unique_code
                        sub['formatted_amount'] = self.env['ir.qweb.field.monetary'].value_to_html(sub['amount'], {'display_currency': move.currency_id})

            # 2. Add Kode Unik as a dedicated "Tax Group" row
            unique_group = {
                'tax_group_name': 'Kode Unik',
                'tax_group_amount': move.amount_unique_code,
                'tax_group_id': self.env.ref('runia_kode_unik_bayar.tax_group_kode_unik').id,
                'formatted_tax_group_amount': self.env['ir.qweb.field.monetary'].value_to_html(move.amount_unique_code, {'display_currency': move.currency_id}),
            }
            
            # Inject into the first subtotal's groups
            if 'groups_by_subtotal' in totals and totals['groups_by_subtotal']:
                first_subtotal_name = list(totals['groups_by_subtotal'].keys())[0]
                totals['groups_by_subtotal'][first_subtotal_name].append(unique_group)
            
            # Re-assign to trigger update
            move.tax_totals = totals

    def action_post(self):
        self._add_unique_code_line()
        return super(AccountMove, self).action_post()

    def _add_unique_code_line(self):
        _logger = logging.getLogger(__name__)
        for move in self:
            if move.move_type != 'out_invoice':
                continue
            
            _logger.info("Checking unique code for invoice %s", move.name)
            # Check if unique code already exists
            product_kode_unik = self.env.ref('runia_kode_unik_bayar.product_product_kode_unik', raise_if_not_found=False)
            if not product_kode_unik:
                _logger.warning("Product product_product_kode_unik not found!")
                return

            # Check if line already exists
            if any(line.product_id == product_kode_unik for line in move.invoice_line_ids):
                _logger.info("Unique code line already exists for invoice %s", move.name)
                continue

            unique_code = self._get_next_unique_code(move.company_id)
            if unique_code == 0:
                _logger.info("Unique code is 0, skipping for invoice %s", move.name)
                continue

            _logger.info("Adding unique code %s to invoice %s", unique_code, move.name)
            self.env['account.move.line'].create({
                'move_id': move.id,
                'product_id': product_kode_unik.id,
                'name': 'Kode Unik Pembayaran',
                'quantity': 1,
                'price_unit': unique_code, # We use price_unit for now, but hide it in totals
                'tax_ids': [(5, 0, 0)],
            })
            # Force recompute
            move.invalidate_recordset(['amount_untaxed', 'amount_tax', 'amount_total', 'amount_unique_code'])
            move._compute_amounts_unique_code()
            if hasattr(move, '_compute_amount'):
                move._compute_amount()
            # _compute_cash_rounding does not exist as a separate method in Odoo 17 account.move

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
