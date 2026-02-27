import frappe


def send_urgent_alert(job_card, manager):

    subject = f"Urgent Job Card {job_card} Needs Technician"

    message = f"""
    <h3>Urgent Job Card Alert</h3>

    <p>Job Card <b>{job_card}</b> is marked as <b>Urgent</b>
    but no technician has been assigned.</p>

    <p>Please assign a technician immediately.</p>
    """

    frappe.sendmail(
        recipients=[manager],
        subject=subject,
        message=message
    )