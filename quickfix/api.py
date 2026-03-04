import frappe
from frappe.client import get_count

@frappe.whitelist()
def share_job_card(job_card_name, customer_email):
    frappe.share.add(
        "Job Card",
        job_card_name,
        customer_email,
        read=1,
        write=0,
        share=0
    )
    
    return f"Job Card {job_card_name} shared with {customer_email}"
@frappe.whitelist()
def manager_only_action():
    frappe.only_for("QF Manager")
    return "This action is allowed only for QF Manager"
@frappe.whitelist()
def get_job_cards_safe():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    job_cards = frappe.get_list(
        "Job Card",
        fields=["name", "customer_name", "status", "assigned_technician", "customer_phone", "customer_email"]
    )

    # Strip sensitive fields for non-managers
    if "QF Manager" not in roles:
        for jc in job_cards:
            jc.pop("customer_phone", None)
            jc.pop("customer_email", None)

    return job_cards
@frappe.whitelist()
def rename_technician(old_name, new_name):

    frappe.rename_doc(
        "Technician",
        old_name,
        new_name,
        merge=False
    )

    return "Technician renamed successfully"

# Using merge=True can merge two different records into one if the target name already exists. 
# This may cause unintended data merging and loss of record separation, leading to data integrity issues.
@frappe.whitelist()
def mark_delivered(job_card):

    doc = frappe.get_doc("Job Card", job_card)

    doc.status = "Delivered"
    doc.save()

    frappe.db.commit()

    return "Delivered"
@frappe.whitelist()
def reject_job(job_card, reason):

    doc = frappe.get_doc("Job Card", job_card)

    doc.status = "Rejected"
    doc.rejection_reason = reason
    doc.save()

    frappe.db.commit()

    return "Rejected"
@frappe.whitelist()
def transfer_technician(job_card, new_technician):

    doc = frappe.get_doc("Job Card", job_card)

    doc.assigned_technician = new_technician
    doc.save()

    frappe.db.commit()

    return "Transferred"
@frappe.whitelist()
def mark_ready(job_card):

    doc = frappe.get_doc("Job Card", job_card)

    doc.status = "Ready for Delivery"
    doc.save()

    frappe.db.commit()

    return "Ready"


@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
    
    # Log to Audit Log
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doctype,
        "action": "count_queried",
        "user": frappe.session.user
    }).insert(ignore_permissions=True)

    # Call original logic
    return get_count(doctype, filters, debug, cache)