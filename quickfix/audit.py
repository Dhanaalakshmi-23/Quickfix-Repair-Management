import frappe

#ignore_permissions=True is used to allow the system to create an Audit Log record automatically whenever a document change occurs.
#This is acceptable because the logging is a system-level tracking mechanism, not initiated directly by a user request, and it prevents permission checks from blocking audit recording.
def log_change(doc, method):
    #frappe.throw("Audit Triggered")
    # Avoid logging Audit Log itself (prevent infinite loop)
    if doc.doctype == "Audit Log":
        return

    audit_doc = frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doc.doctype,
        "document_name": doc.name,
        "action": method,
        "user": frappe.session.user,
        "timestamp": frappe.utils.now()
    })

    audit_doc.insert(ignore_permissions=True)