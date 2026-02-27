import frappe


def send_urgent_alert(job_card, manager):

    frappe.log_error(
        title="Urgent Job Without Technician",
        message=f"Job Card {job_card} is marked as Urgent but has no technician assigned."
    )

    frappe.msgprint(
        f"Urgent alert triggered for Job Card {job_card}"
    )