import frappe
from frappe.client import get_count
from frappe.types.filter import date
import qrcode
import base64
from io import BytesIO



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


@frappe.whitelist()
def prepare_technician_performance_report():

    frappe.enqueue(
        method="frappe.core.doctype.prepared_report.prepared_report.run_background",
        queue="long",
        timeout=600,
        report_name="Technician Performance Report",
        filters={}
    )

    return "Report preparation started in background."

# This API endpoint is used to fetch data for the status chart on the dashboard. It retrieves the count of job cards grouped by their status and formats it for use in a chart.
@frappe.whitelist()
def get_status_chart_data():
    
    data = frappe.db.sql("""
        SELECT status, COUNT(name)
        FROM `tabJob Card`
        GROUP BY status
    """, as_list=1)

    labels = []
    values = []

    for d in data:
        labels.append(d[0])
        values.append(d[1])

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Job Cards",
                "values": values
            }
        ]
    }

#jinja method to get shop name, used in website templates and reports
def get_shop_name():
    return "QuickFix Device Repair Shop"
def get_job_card_qr(job_card_name):

    url = frappe.utils.get_url(f"/app/job-card/{job_card_name}")

    qr = qrcode.make(url)

    buffered = BytesIO()
    qr.save(buffered, format="PNG")

    img_str = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"

#Email notification when job is ready for pickup
def send_job_ready_email(job_card):

    # Get Job Card document
    doc = frappe.get_doc("Job Card", job_card)

    # Send email to customer
    frappe.sendmail(
        recipients=["dhanaalakshminarayanan@gmail.com"],
        subject="Your Job is Ready",
        message="Your service job is completed and ready for pickup."
    )

#monthly revenue report generation, can be scheduled via hooks.py
def generate_monthly_revenue_report(month):

    # Get all delivered jobs
    jobs = frappe.get_all(
        "Job Card",
        filters={"status": "Delivered"},
        fields=["total_amount"]
    )

    total_revenue = 0

    for job in jobs:
        total_revenue += job.total_amount

    frappe.log_error(
        title="Monthly Revenue Report",
        message=f"Total Revenue for {month}: {total_revenue}"
    )
def enqueue_monthly_report(month):

    frappe.enqueue(
        "quickfix.api.generate_monthly_revenue_report",
        month=month,
        queue="long",
        timeout=600
    )

#Used for testing the custom api method
@frappe.whitelist()
def get_job_summary():
    
    job_card_name = frappe.form_dict.get("job_card_name")

    if not job_card_name:
        frappe.response.http_status_code = 400
        return {"error": "job_card_name is required"}

    if not frappe.db.exists("Job Card", job_card_name):
        frappe.response.http_status_code = 404
        return {"error": "Not found"}

    job = frappe.get_doc("Job Card", job_card_name)

    return {
        "job_card": job.name,
        "status": job.status,
        "priority": job.priority,
        "creation_date": date.today()
    }


# Api to check Rate limiting & abuse protection
@frappe.whitelist(allow_guest=True)
def get_job_by_phone():

    phone = frappe.form_dict.get("phone")

    # get client IP
    ip = frappe.local.request_ip

    cache = frappe.cache()

    key = f"rate_limit:{ip}"

    count = cache.get_value(key)

    if not count:
        count = 0

    count = int(count)

    if count >= 2:
        frappe.response.http_status_code = 429
        return {"error": "Rate limit exceeded. Try again later."}

    # increment counter
    cache.set_value(key, count + 1, expires_in_sec=60)

    job = frappe.db.get_value(
        "Job Card",
        {"customer_phone": phone},
        ["name", "status", "priority"],
        as_dict=True
    )

    if not job:
        frappe.response.http_status_code = 404
        return {"error": "Job not found"}

    return job