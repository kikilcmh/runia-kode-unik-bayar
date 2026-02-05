from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    unique_code_limit = fields.Integer(
        string="Batas Kode Unik",
        default=500
    )
    last_code = fields.Integer(
        string="Kode Terakhir",
        default=0
    )

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    unique_code_limit = fields.Integer(
        string="Batas Kode Unik",
        related='company_id.unique_code_limit',
        readonly=False,
    )
    last_code = fields.Integer(
        string="Kode Terakhir",
        related='company_id.last_code',
        readonly=True,
    )
