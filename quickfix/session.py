import frappe

def on_session_creation(login_manager):
    create_audit_log("Login")

def on_logout(login_manager):
    create_audit_log("Logout")

def create_audit_log(action):
    if frappe.flags.in_migrate:
        return

    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "User",
        "document_name": frappe.session.user,
        "action": action,
        "user": frappe.session.user,
        "timestamp": frappe.utils.now()
    }).insert(ignore_permissions=True)