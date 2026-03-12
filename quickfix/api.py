import frappe
from frappe.client import get_count
from frappe.types.filter import date
import qrcode
import base64
from io import BytesIO
from frappe.query_builder import DocType
from frappe.utils import now_datetime, add_days
import hmac
import hashlib
import json,re

def get_status_chart_datas():

    cache = frappe.cache()
    cache_key = "job_card_status_chart"

    # check cache first
    data = cache.get_value(cache_key)

    if data:
        return data

    # if not cached, run DB query
    data = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabJob Card`
        GROUP BY status
    """, as_dict=True)

    # store in cache for 300 seconds
    cache.set_value(cache_key, data, expires_in_sec=300)

    return data


@frappe.whitelist()
def get_overdue_jobs():

    JC = DocType("Job Card")

    seven_days_ago = add_days(now_datetime(), -7)

    result = (
        frappe.qb
        .from_(JC)
        .select(
            JC.name,
            JC.customer_name,
            JC.assigned_technician,
            JC.creation
        )
        .where(
            (JC.status.isin(["Pending Diagnosis", "In Repair"])) &
            (JC.creation < seven_days_ago)
        )
        .orderby(JC.creation)
        .run(as_dict=True)
    )

    return result


@frappe.whitelist()
def transfer_job(from_tech, to_tech):

    try:

        frappe.db.sql("""
            UPDATE `tabJob Card`
            SET assigned_technician = %s
            WHERE assigned_technician = %s
            AND status IN ('Pending Diagnosis','In Repair')
        """, (to_tech, from_tech))

        frappe.db.commit()

        return "Jobs transferred successfully"

    except Exception:

        frappe.db.rollback()

        frappe.log_error(
            frappe.get_traceback(),
            "Job Transfer Failed"
        )

        raise

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

#ignore_permissions=True is used to insert an Audit Log entry whenever the custom count function is called, ensuring the query activity is recorded.
#This bypass is acceptable because it is system-generated logging for monitoring purposes, not a direct user operation on the Audit Log.
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
        SELECT status, COUNT(name) as count
        FROM `tabJob Card`
        GROUP BY status
    """, as_dict=True)

    labels = []
    values = []

    for row in data:
        labels.append(row.status)
        values.append(row.count)

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


#ignore_permissions=True is used to update the Job Card payment status and create an Audit Log entry after verifying the payment webhook.
#This is acceptable because the update is triggered by a trusted external payment system after signature verification, making it a system-driven action rather than a normal user request.
@frappe.whitelist(allow_guest=True)
def payment_webhook():

    payload = frappe.request.data

    secret = frappe.conf.get("payment_webhook_secret", "")

    signature = frappe.get_request_header("X-Signature")

    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature or ""):
        frappe.throw("Invalid signature", frappe.AuthenticationError)

    data = json.loads(payload)

    if frappe.db.exists(
        "Audit Log",
        {"action": "payment_received", "document_name": data["ref"]}
    ):
        return {"status": "duplicate", "message": "Already processed"}

    job = frappe.get_doc("Job Card", data["ref"])

    job.payment_status = "Paid"
    job.save(ignore_permissions=True)

    frappe.get_doc({
        "doctype": "Audit Log",
        "action": "payment_received",
        "document_type": "Job Card",
        "document_name": data["ref"]
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    return {"status": "ok"}


logger = frappe.logger("quickfix")

@frappe.whitelist()
def send_webhook(job_card_name):
    logger.info(f"Webhook triggered for {job_card_name}")
    
    settings = frappe.get_single("QuickFix Settings")
    if not settings.webhook_url:
        logger.warning(f"No webhook URL configured, skipping for {job_card_name}")
        return

    import requests
    try:
        doc = frappe.get_doc("Job Card", job_card_name)
        payload = {
            "event": "job_submitted",
            "job_card": doc.name,
            "amount": doc.final_amount
        }
        r = requests.post(settings.webhook_url, json=payload, timeout=5)
        r.raise_for_status()
        logger.info(f"Webhook sent successfully for {job_card_name}")

    except Exception as e:
        logger.error(f"Webhook failed for {job_card_name}: {e}")
        frappe.log_error(
            title="Webhook Error",
            message=frappe.get_traceback()
        )

@frappe.whitelist()
def trigger_test_error():
    frappe.enqueue(
        "quickfix.api.failing_background_job",
        queue="short"
    )

def failing_background_job():
    raise Exception("Test background job failure for M3")

#N1 - Unsafe API endpoint vulnerable to SQL Injection
@frappe.whitelist(allow_guest=True)
def get_job_by_phone_unsafe(customer_phone):

    query = f"""
        SELECT name, status
        FROM `tabJob Card`
        WHERE customer_phone = '{customer_phone}'
    """

    result = frappe.db.sql(query, as_dict=True)

    return result
#N1 - Safe version of the API endpoint using parameterized queries to prevent SQL Injection
@frappe.whitelist(allow_guest=True)
def get_job_by_phone_safe(customer_phone):

    query = """
        SELECT name, status
        FROM `tabJob Card`
        WHERE customer_phone = %s
    """

    result = frappe.db.sql(query, (customer_phone,), as_dict=True)

    return result


@frappe.whitelist(allow_guest=True)
def track_job(customer_phone):

 
    customer_phone = re.sub(r"\D", "", customer_phone)

    if len(customer_phone) > 10:
        frappe.throw("Invalid phone number")

    # rate limiting
    ip = frappe.local.request_ip
    cache = frappe.cache()

    key = f"rate_limit:{ip}"

    count = cache.get_value(key) or 0
    count = int(count)

    if count > 50:
        frappe.throw("Too many requests. Try again later.")

    cache.set_value(key, count + 1, expires_in_sec=60)

    # check job existence
    jobs = frappe.get_all(
        "Job Card",
        filters={"customer_phone": customer_phone},
        fields=["name", "status"]
    )

    if not jobs:
        frappe.throw("No job found for this phone number")

    return jobs