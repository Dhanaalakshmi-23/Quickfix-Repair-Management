# Copyright (c) 2026, DhanaaLakshmi and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class JobCard(Document):

    def before_save(self):
        if self.labour_charge is None:
            default_labor = frappe.db.get_single_value(
                "QuickFix Settings",
                "default_labour_charge"
            )
            self.labour_charge = default_labor

