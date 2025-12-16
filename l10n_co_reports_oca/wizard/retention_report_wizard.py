from odoo import api, fields, models


class RetentionReportWizardAbstract(models.AbstractModel):
    """Abstract wizard for Colombian retention reports."""

    _name = "l10n_co_reports_oca.retention_report.wizard.abstract"
    _description = "Colombian Retention Report Wizard Abstract"
    _inherit = "account_financial_report_abstract_wizard"

    date_range_id = fields.Many2one(
        comodel_name="date.range",
        string="Date Range",
    )
    date_from = fields.Date(
        string="Start Date",
        required=True,
    )
    date_to = fields.Date(
        string="End Date",
        required=True,
    )
    target_move = fields.Selection(
        selection=[
            ("posted", "All Posted Entries"),
            ("all", "All Entries"),
        ],
        string="Target Moves",
        required=True,
        default="posted",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Filter Partners",
        default=lambda self: self._default_partners(),
    )
    expedition_date = fields.Date(
        string="Expedition Date",
        default=fields.Date.context_today,
        required=True,
        help="Date when the certificate is issued",
    )
    declaration_date = fields.Date(
        string="Declaration Date",
        default=fields.Date.context_today,
        required=True,
        help="Date of the tax declaration",
    )
    article = fields.Char(
        string="Article",
        default="ART. 10 DECRETO 386/91",
        required=True,
        help="Legal article reference",
    )

    @api.onchange("date_range_id")
    def _onchange_date_range_id(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    def _prepare_report_data(self):
        self.ensure_one()
        res = super()._prepare_report_data()
        res.update(
            {
                "date_from": self.date_from,
                "date_to": self.date_to,
                "target_move": self.target_move,
                "partner_ids": self.partner_ids.ids,
                "company_id": self.company_id.id,
                "expedition_date": self.expedition_date,
                "declaration_date": self.declaration_date,
                "article": self.article,
            }
        )
        return res

    def _export(self, report_type):
        """Export report in the given format."""
        self.ensure_one()
        data = self._prepare_report_data()
        report_name = self._get_report_name(report_type)
        return (
            self.env["ir.actions.report"]
            .search(
                [
                    ("report_name", "=", report_name),
                    ("report_type", "=", report_type),
                ],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _get_report_name(self, report_type="qweb-html"):
        """To be overridden in child classes."""
        raise NotImplementedError()


class RetentionReportWizardIca(models.TransientModel):
    """Wizard for ICA retention certificate."""

    _name = "l10n_co_reports_oca.retention_report.wizard.ica"
    _description = "Colombian ICA Retention Report Wizard"
    _inherit = "l10n_co_reports_oca.retention_report.wizard.abstract"

    def _get_report_name(self, report_type="qweb-html"):
        if report_type == "xlsx":
            return "l10n_co_reports_oca.report_certification_ica_xlsx"
        return "l10n_co_reports_oca.report_certification_ica"


class RetentionReportWizardIva(models.TransientModel):
    """Wizard for IVA retention certificate."""

    _name = "l10n_co_reports_oca.retention_report.wizard.iva"
    _description = "Colombian IVA Retention Report Wizard"
    _inherit = "l10n_co_reports_oca.retention_report.wizard.abstract"

    def _get_report_name(self, report_type="qweb-html"):
        if report_type == "xlsx":
            return "l10n_co_reports_oca.report_certification_iva_xlsx"
        return "l10n_co_reports_oca.report_certification_iva"


class RetentionReportWizardFuente(models.TransientModel):
    """Wizard for Fuente (Source) retention certificate."""

    _name = "l10n_co_reports_oca.retention_report.wizard.fuente"
    _description = "Colombian Fuente Retention Report Wizard"
    _inherit = "l10n_co_reports_oca.retention_report.wizard.abstract"

    def _get_report_name(self, report_type="qweb-html"):
        if report_type == "xlsx":
            return "l10n_co_reports_oca.report_certification_fuente_xlsx"
        return "l10n_co_reports_oca.report_certification_fuente"
