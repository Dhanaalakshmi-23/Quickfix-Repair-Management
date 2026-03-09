import frappe
from frappe.utils import today,now


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

# Jinja Method
def get_shop_name():
    settings = frappe.get_single("QuickFix Settings")
    return settings.shop_name if settings else ""


# Jinja Filter
def format_job_id(value):
    if not value:
        return ""
    return f"JOB#{value}"



def check_low_stock():

    last_run = frappe.db.sql("""
        SELECT name
        FROM `tabAudit Log`
        WHERE action='low_stock_check'
        AND DATE(timestamp)=%s
        LIMIT 1
    """, (today(),))

    if last_run:
        print("Already ran today")
        return

    print("Checking low stock items...")

    frappe.get_doc({
        "doctype": "Audit Log",
        "action": "low_stock_check",
        "doctype_name": "System",
        "document_name": "Daily Low Stock Check",
        "user": "Administrator",
        "timestamp": now()   
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    print("Job completed")