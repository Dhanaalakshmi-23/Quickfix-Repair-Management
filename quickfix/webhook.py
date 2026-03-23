import frappe
import requests
import json
import hashlib


# `ignore_permissions=True` is used to insert an Audit Log record after a webhook is successfully sent, ensuring the system records the event even if the current user lacks permission.
# This is acceptable because the logging happens as part of a background system process (webhook handling) rather than a direct user action.

def send_webhook(job_card_name, retry_count=0):

    settings = frappe.get_single("QuickFix Settings")

    if not settings.webhook_url:
        return

    doc = frappe.get_doc("Job Card", job_card_name)

    payload = {
        "event": "job_submitted",
        "job_card": doc.name,
        "customer": doc.customer_name,
        "amount": doc.final_amount
    }

    webhook_id = hashlib.sha256(
        f"{doc.name}-job_submitted".encode()
    ).hexdigest()

    # Deduplication check
    if frappe.db.exists("Audit Log", {"method": webhook_id}):
        return

    try:

        r = requests.post(settings.webhook_url, json=payload, timeout=5)
        r.raise_for_status()

        frappe.get_doc({
            "doctype": "Audit Log",
            "method": webhook_id,
            "status": "Success",
            "document_type": "Job Card",
            "document_name": doc.name
        }).insert(ignore_permissions=True)

    except Exception as e:

        frappe.log_error(str(e), "Webhook Error")

        if retry_count < 3:
            frappe.enqueue(
                "quickfix.webhooks.send_webhook",
                job_card_name=job_card_name,
                retry_count=retry_count + 1,
                queue="short",
                enqueue_after_commit=True,
                timeout=300,
                now=False,
                job_name=f"webhook_retry_{retry_count}",
                enqueue_at=frappe.utils.now_datetime()
            )
