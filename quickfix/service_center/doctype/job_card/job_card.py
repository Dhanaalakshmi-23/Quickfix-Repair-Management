# Copyright (c) 2026, DhanaaLakshmi and contributors
# For license information, please see license.txt
import re

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

    def validate(self):
        if self.customer_phone:
            if not re.fullmatch(r"\d{10}",self.customer_phone):
                frappe.throw("Customer phone number must be 10 digits")
    
        repair_statuses = ["In Repair", "Ready for Delivery", "Completed"]

        if self.status in repair_statuses and not self.assigned_technician:
            frappe.throw("Assigned Technician is required when status is In Repair or beyond")

        parts_total = 0
        for row in self.parts_used:
            row.total_price = (row.quantity or 0) * (row.unit_price or 0)
            parts_total += row.total_price

        self.parts_total = parts_total

        if not self.labour_charge:
            self.labour_charge = frappe.db.get_single_value(
                "QuickFix Settings",
                "labour_charge"
            ) or 0

        self.final_amount = (self.parts_total or 0) + (self.labour_charge or 0)

    def before_submit(self):

        if self.status != "Ready for Delivery":
            frappe.throw("Job Card can only be submitted when status is 'Ready for Delivery'")

        for row in self.parts_used:

            if not row.part:
                continue

            stock_qty = frappe.db.get_value(
                "Spare Part",
                row.part,
                "stock_qty"
            ) or 0

            if stock_qty < (row.quantity or 0):
                frappe.throw(
                    f"Not enough stock for Part {row.part}. "
                    f"Available: {stock_qty}, Required: {row.quantity}"
                )
    def on_submit(self):
        # Reduce stock for used parts
        for row in self.parts_used:
            if not row.part:
                continue
            current_stock = frappe.db.get_value(
                "Spare Part",
                row.part,
                "stock_qty"
            ) or 0
            frappe.db.set_value(
                "Spare Part",
                row.part,
                "stock_qty",
                current_stock - (row.quantity or 0),
                update_modified=False
            )
        invoice = frappe.get_doc({
        "doctype": "Service Invoice",
        "job_card": self.name,
        "customer_name": self.customer_name,
        "amount": self.final_amount
    })

        invoice.insert(ignore_permissions=True)
        frappe.publish_realtime(
        "job_ready",
        {
            "job_card": self.name,
            "message": "Your device is ready for delivery"
        },
        user=self.owner
    )
        frappe.enqueue(
        "quickfix.api.send_job_ready_email",
        job_card=self.name
    )



    def on_cancel(self):
        self.db_set("status", "Cancelled")

        for row in self.parts_used:
            if not row.part:
                continue

            current_stock = frappe.db.get_value(
                "Spare Part",
                row.part,
                "stock_qty"
            ) or 0

            frappe.db.set_value(
                "Spare Part",
                row.part,
                "stock_qty",
                current_stock + (row.quantity or 0),
            )
        
        invoice_name = frappe.db.get_value(
            "Service Invoice",
            {"job_card": self.name},
            "name"
        )
        if invoice_name:
            invoice_doc = frappe.get_doc("Service Invoice", invoice_name)
            if invoice_doc.docstatus == 1:  
                invoice_doc.cancel()

    def on_trash(self):
        if self.docstatus not in ["Draft", "Cancelled"]:
            frappe.throw("Only Job Cards in Draft or Cancelled state can be deleted")

    def on_update(self):
        pass
