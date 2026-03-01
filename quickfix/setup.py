import frappe

def after_install():
    create_default_device_types()
    create_default_settings()
    frappe.msgprint("QuickFix installed successfully with default setup.")

def create_default_device_types():
        default_types = ["Smartphone", "Laptop", "Tablet"]

        for device in default_types:
            if not frappe.db.exists("Device Type", device):
                frappe.get_doc({
                    "doctype": "Device Type",
                    "device_type_name": device
                }).insert(ignore_permissions=True)

def create_default_settings():
    if not frappe.db.exists("QuickFix Settings"):
        frappe.get_doc({
            "doctype": "QuickFix Settings",
            "shop_name": "QuickFix Repair Center",
            "manager_email": "manager@quickfix.com"
        }).insert(ignore_permissions=True)

def before_uninstall():
    if frappe.db.exists("Job Card", {"docstatus": 1}):
        frappe.throw(
            "Cannot uninstall QuickFix. Submitted Job Cards exist.",
            frappe.ValidationError
        )