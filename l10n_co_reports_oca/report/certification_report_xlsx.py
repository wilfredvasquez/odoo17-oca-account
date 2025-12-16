# Copyright 2024 Alejandro Cora González
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class CertificationReportXlsxAbstract(models.AbstractModel):
    """Abstract XLSX report for Colombian retention certificates."""

    _name = "report.l10n_co_reports_oca.certification_report_xlsx_abstract"
    _description = "Colombian Certification Report XLSX Abstract"
    _inherit = "report.account_financial_report.abstract_report_xlsx"

    def _get_report_name(self, report, data=False):
        return "Certificado de Retención"

    def _get_report_columns(self, report):
        raise NotImplementedError()

    def _get_report_filters(self, report):
        return [
            ["Fecha Desde", str(report.date_from)],
            ["Fecha Hasta", str(report.date_to)],
            ["Empresa", report.company_id.name],
            ["Movimientos", "Publicados" if report.target_move == "posted" else "Todos"],
        ]

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 3

    def _get_col_pos_initial_balance_label(self):
        return 0

    def _get_col_count_final_balance_name(self):
        return 1

    def _get_col_pos_final_balance_label(self):
        return 0

    def _get_report_data(self, report, data):
        """Get report data - to be implemented by child classes."""
        raise NotImplementedError()

    def _generate_report_content(self, workbook, report, data, report_data):
        """Generate XLSX content."""
        # Get the report data
        partners_data = self._get_report_data(report, data)

        for partner_id, partner_info in partners_data.items():
            partner = partner_info["partner"]

            # Write partner header
            self.write_array_title(
                f"{partner.display_name} - NIT: {partner.vat or 'N/A'}",
                report_data,
            )

            # Write column headers
            self.write_array_header(report_data)

            # Write lines
            for line in sorted(partner_info["lines_per_group"].values(), key=lambda x: x.get("name", "")):
                self.write_line_from_dict(line, report_data)

            # Write totals
            totals = partner_info.get("totals", {})
            totals["name"] = "TOTAL"
            self.write_line_from_dict(totals, report_data)

            # Add empty row between partners
            report_data["row_pos"] += 2


class CertificationReportIcaXlsx(models.AbstractModel):
    """ICA retention certificate XLSX report."""

    _name = "report.l10n_co_reports_oca.report_certification_ica_xlsx"
    _description = "Colombian ICA Certification Report XLSX"
    _inherit = "report.l10n_co_reports_oca.certification_report_xlsx_abstract"

    def _get_report_name(self, report, data=False):
        return self._get_report_complete_name(
            report, "Certificado Retención ICA", data
        )

    def _get_report_columns(self, report):
        return {
            0: {"header": "Bimestre", "field": "name", "width": 25},
            1: {
                "header": "Monto del pago sujeto a retención",
                "field": "tax_base_amount",
                "type": "amount",
                "width": 25,
            },
            2: {
                "header": "Retenido y consignado",
                "field": "balance",
                "type": "amount",
                "width": 20,
            },
        }

    def _get_report_data(self, report, data):
        """Get ICA report data."""
        report_model = self.env["report.l10n_co_reports_oca.report_certification_ica"]
        return report_model._get_report_data(data)


class CertificationReportIvaXlsx(models.AbstractModel):
    """IVA retention certificate XLSX report."""

    _name = "report.l10n_co_reports_oca.report_certification_iva_xlsx"
    _description = "Colombian IVA Certification Report XLSX"
    _inherit = "report.l10n_co_reports_oca.certification_report_xlsx_abstract"

    def _get_report_name(self, report, data=False):
        return self._get_report_complete_name(
            report, "Certificado Retención IVA", data
        )

    def _get_report_columns(self, report):
        return {
            0: {"header": "Bimestre", "field": "name", "width": 25},
            1: {
                "header": "Monto Total Operación",
                "field": "tax_base_amount",
                "type": "amount",
                "width": 20,
            },
            2: {
                "header": "Monto del Pago Sujeto Retención",
                "field": "balance_15_over_19",
                "type": "amount",
                "width": 25,
            },
            3: {
                "header": "Retenido Consignado",
                "field": "balance",
                "type": "amount",
                "width": 20,
            },
            4: {
                "header": "%",
                "field": "percentage",
                "type": "amount",
                "width": 10,
            },
        }

    def _get_report_data(self, report, data):
        """Get IVA report data."""
        report_model = self.env["report.l10n_co_reports_oca.report_certification_iva"]
        return report_model._get_report_data(data)


class CertificationReportFuenteXlsx(models.AbstractModel):
    """Fuente retention certificate XLSX report."""

    _name = "report.l10n_co_reports_oca.report_certification_fuente_xlsx"
    _description = "Colombian Fuente Certification Report XLSX"
    _inherit = "report.l10n_co_reports_oca.certification_report_xlsx_abstract"

    def _get_report_name(self, report, data=False):
        return self._get_report_complete_name(
            report, "Certificado Retención Fuente", data
        )

    def _get_report_columns(self, report):
        return {
            0: {"header": "Concepto de retención", "field": "name", "width": 40},
            1: {
                "header": "Monto del pago sujeto a retención",
                "field": "tax_base_amount",
                "type": "amount",
                "width": 25,
            },
            2: {
                "header": "Retenido y consignado",
                "field": "balance",
                "type": "amount",
                "width": 20,
            },
        }

    def _get_report_data(self, report, data):
        """Get Fuente report data."""
        report_model = self.env["report.l10n_co_reports_oca.report_certification_fuente"]
        return report_model._get_report_data(data)
