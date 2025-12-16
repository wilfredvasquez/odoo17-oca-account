{
    "name": "Colombian - Accounting Reports (OCA)",
    "version": "17.0.1.0.0",
    "category": "Accounting/Localizations/Reporting",
    "summary": "Colombian retention certificates for Odoo Community",
    "license": "AGPL-3",
    "depends": [
        "l10n_co",
        "account_financial_report",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/retention_report_wizard_views.xml",
        "report/certification_report_templates.xml",
        "data/menuitem.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
