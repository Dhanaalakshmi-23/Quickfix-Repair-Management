import frappe

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

def manager_only_action():
    frappe.only_for("QF Manager")
    return "This action is allowed only for QF Manager"

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