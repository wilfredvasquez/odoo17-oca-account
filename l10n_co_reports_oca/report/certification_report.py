from odoo import api, models


class CertificationReportAbstract(models.AbstractModel):
    """Abstract report for Colombian retention certificates."""

    _name = "report.l10n_co_reports_oca.certification_report_abstract"
    _description = "Colombian Certification Report Abstract"
    _inherit = "report.account_financial_report.abstract_report"

    BIMONTH_NAMES = {
        1: "Enero - Febrero",
        2: "Marzo - Abril",
        3: "Mayo - Junio",
        4: "Julio - Agosto",
        5: "Septiembre - Octubre",
        6: "Noviembre - Diciembre",
    }

    def _get_bimonth_for_date(self, date):
        """Calculate bimonth (1-6) from a date."""
        # month:   1   2   3   4   5   6   7   8   9   10  11   12
        # bimonth: \ 1 /   \ 2 /   \ 3 /   \ 4 /   \ 5 /    \ 6 /
        return (date.month + 1) // 2

    def _get_bimonth_name(self, bimonth_index):
        """Get the Spanish name for a bimonth."""
        return self.BIMONTH_NAMES.get(bimonth_index, "")

    def _get_base_domain(self, data):
        """Build base domain for account.move.line search."""
        domain = [
            ("partner_id", "!=", False),
            ("company_id", "=", data["company_id"]),
        ]

        # Filter by posted moves or all
        if data.get("target_move") == "posted":
            domain.append(("parent_state", "=", "posted"))
        else:
            domain.append(("parent_state", "not in", ("draft", "cancel")))

        # Date filters
        if data.get("date_from"):
            domain.append(("date", ">=", data["date_from"]))
        if data.get("date_to"):
            domain.append(("date", "<=", data["date_to"]))

        # Partner filter
        if data.get("partner_ids"):
            domain.append(("partner_id", "in", data["partner_ids"]))

        return domain

    def _get_account_domain(self):
        """To be overridden in child classes."""
        raise NotImplementedError()

    def _handle_aml(self, aml, lines_per_group):
        """Process an account.move.line. To be overridden in child classes."""
        raise NotImplementedError()

    def _get_report_data(self, data):
        """Get report data grouped by partner."""
        domain = self._get_base_domain(data)
        domain.extend(self._get_account_domain())

        amls = self.env["account.move.line"].search(domain, order="partner_id, id")

        partners_data = {}
        for aml in amls:
            partner = aml.partner_id
            if partner.id not in partners_data:
                partners_data[partner.id] = {
                    "partner": partner,
                    "lines_per_group": {},
                    "totals": {},
                }

            self._handle_aml(aml, partners_data[partner.id]["lines_per_group"])

        # Calculate totals for each partner
        for partner_id, partner_data in partners_data.items():
            self._calculate_partner_totals(partner_data)

        return partners_data

    def _calculate_partner_totals(self, partner_data):
        """Calculate totals for a partner's lines."""
        totals = {}
        for group_key, values in partner_data["lines_per_group"].items():
            for field, value in values.items():
                if isinstance(value, (int, float)):
                    totals[field] = totals.get(field, 0) + value
        partner_data["totals"] = totals

    def _get_report_values(self, docids, data):
        """Generate report values for Qweb template."""
        res = super()._get_report_values(docids, data)
        wizard = self.env[data["wizard_name"]].browse(data["wizard_id"])

        partners_data = self._get_report_data(data)

        # Convert to list format for template
        docs = []
        for partner_id, partner_data in partners_data.items():
            lines = []
            for group_key, values in sorted(partner_data["lines_per_group"].items()):
                lines.append(values)

            if lines:  # Only include partners with lines
                docs.append(
                    {
                        "partner": partner_data["partner"],
                        "lines": lines,
                        "totals": partner_data["totals"],
                    }
                )

        # Get fiscal year from declaration date or date_to
        current_date = data.get("declaration_date") or data.get("date_to")
        if current_date:
            fiscal_year_dates = wizard.company_id.compute_fiscalyear_dates(current_date)
            current_year = fiscal_year_dates["date_from"].year
        else:
            current_year = wizard.date_to.year if wizard.date_to else False

        res.update(
            {
                "docs": docs,
                "wizard": wizard,
                "company": wizard.company_id,
                "current_year": current_year,
                "expedition_date": data.get("expedition_date"),
                "declaration_date": data.get("declaration_date"),
                "article": data.get("article"),
            }
        )
        return res


class CertificationReportIca(models.AbstractModel):
    """ICA retention certificate report."""

    _name = "report.l10n_co_reports_oca.report_certification_ica"
    _description = "Colombian ICA Certification Report"
    _inherit = "report.l10n_co_reports_oca.certification_report_abstract"

    def _get_account_domain(self):
        """Filter for ICA retention accounts (2368%)."""
        return [("account_id.code", "=like", "2368%")]

    def _handle_aml(self, aml, lines_per_group):
        """Process AML for ICA report, grouped by bimonth."""
        bimonth = self._get_bimonth_for_date(aml.date)

        if bimonth not in lines_per_group:
            lines_per_group[bimonth] = {
                "name": self._get_bimonth_name(bimonth),
                "tax_base_amount": 0.0,
                "balance": 0.0,
            }

        # Balance: credit - debit
        lines_per_group[bimonth]["balance"] += aml.credit - aml.debit

        # Tax base amount
        if aml.credit:
            lines_per_group[bimonth]["tax_base_amount"] += aml.tax_base_amount
        else:
            lines_per_group[bimonth]["tax_base_amount"] -= aml.tax_base_amount


class CertificationReportIva(models.AbstractModel):
    """IVA retention certificate report."""

    _name = "report.l10n_co_reports_oca.report_certification_iva"
    _description = "Colombian IVA Certification Report"
    _inherit = "report.l10n_co_reports_oca.certification_report_abstract"

    def _get_account_domain(self):
        """Filter for IVA retention accounts (2367% or 2408%)."""
        return [
            "|",
            ("account_id.code", "=like", "2367%"),
            ("account_id.code", "=like", "2408%"),
        ]

    def _handle_aml(self, aml, lines_per_group):
        """Process AML for IVA report, grouped by bimonth."""
        bimonth = self._get_bimonth_for_date(aml.date)

        if bimonth not in lines_per_group:
            lines_per_group[bimonth] = {
                "name": self._get_bimonth_name(bimonth),
                "tax_base_amount": 0.0,
                "balance": 0.0,
                "balance_15_over_19": 0.0,
                "percentage": 0.15,
            }

        # 2408% accounts go to balance_15_over_19
        if aml.account_id.code.startswith("2408"):
            lines_per_group[bimonth]["balance_15_over_19"] += aml.credit - aml.debit
        else:
            # 2367% accounts
            lines_per_group[bimonth]["balance"] += aml.credit - aml.debit
            if aml.credit:
                lines_per_group[bimonth]["tax_base_amount"] += aml.tax_base_amount
            else:
                lines_per_group[bimonth]["tax_base_amount"] -= aml.tax_base_amount

    def _calculate_partner_totals(self, partner_data):
        """Calculate totals for IVA report, including percentage."""
        super()._calculate_partner_totals(partner_data)
        # Set percentage in totals
        if partner_data["totals"].get("balance"):
            partner_data["totals"]["percentage"] = 0.15
        else:
            partner_data["totals"]["percentage"] = 0


class CertificationReportFuente(models.AbstractModel):
    """Fuente (Source) retention certificate report."""

    _name = "report.l10n_co_reports_oca.report_certification_fuente"
    _description = "Colombian Fuente Certification Report"
    _inherit = "report.l10n_co_reports_oca.certification_report_abstract"

    def _get_account_domain(self):
        """Filter for Fuente retention accounts (2365% except 236505)."""
        return [
            ("account_id.code", "=like", "2365%"),
            ("account_id.code", "!=", "236505"),
        ]

    def _handle_aml(self, aml, lines_per_group):
        """Process AML for Fuente report, grouped by account."""
        account_code = aml.account_id.code

        if account_code not in lines_per_group:
            lines_per_group[account_code] = {
                "name": aml.account_id.display_name,
                "tax_base_amount": 0.0,
                "balance": 0.0,
            }

        # Balance: credit - debit
        lines_per_group[account_code]["balance"] += aml.credit - aml.debit

        # Tax base amount
        if aml.credit:
            lines_per_group[account_code]["tax_base_amount"] += aml.tax_base_amount
        else:
            lines_per_group[account_code]["tax_base_amount"] -= aml.tax_base_amount
