import frappe

def job_card_query_conditions(user):
    if "QF Technician" in frappe.get_roles(user):
        return f"`tabJob Card`.assigned_technician = '{user}'"
    return None

def service_invoice_has_permission(doc, user):
    if "QF Manager" in frappe.get_roles(user):
        return True

    job_card = frappe.get_doc("Job Card", doc.job_card)

    if job_card.payment_status != "Paid":
        return False

    return True