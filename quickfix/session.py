import frappe

def on_session_creation(login_manager):
    create_audit_log("Login")

def on_logout(login_manager):
    create_audit_log("Logout")

#ignore_permissions=True is used to ensure an Audit Log entry is created whenever a user action occurs, even if the user does not have permission to create Audit Log records.
#This is acceptable because the logging is a system-level tracking mechanism used for monitoring and auditing user activities.
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