import frappe

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