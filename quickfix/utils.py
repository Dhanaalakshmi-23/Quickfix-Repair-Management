import frappe
from frappe.utils import today,now
import uuid


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

    start = today() + " 00:00:00"
    end = today() + " 23:59:59"

    last_run = frappe.db.get_value(
        "Audit Log",
        {
            "action": "low_stock_check",
            "timestamp": ["between", [start, end]]
        },
        "name"
    )

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



# Example of a failing background job for testing
def failing_background_job():
    frappe.logger().info("Starting failing background job")

    # deliberately cause failure
    raise Exception("Intentional Failure for Testing Background Job")

def run_failure_test():
    frappe.enqueue(
        "quickfix.utils.failing_background_job",
        queue="short"
    )


def cancel_old_draft_job_cards():

    frappe.db.sql("""
        UPDATE `tabJob Card`
        SET status = 'Cancelled'
        WHERE status = 'Draft'
        LIMIT 1000
    """)

    # frappe.db.commit()

    print("1000 Draft Job Cards marked as Cancelled")



def insert_audit_logs_bulk():

    logs = []

    for i in range(500):
        logs.append((
            str(uuid.uuid4()),  # name
            "Cancel Job Card",  # action
            frappe.session.user # user
        ))

    frappe.db.bulk_insert(
        "Audit Log",
        ["name", "action", "user"],
        logs
    )

    # frappe.db.commit()

    print("500 Audit Logs inserted using bulk_insert")