import frappe

def get_context(context):

    job_id = frappe.form_dict.get("job_id")

    context.title = "Track Repair Job"
    context.description = "Track your device repair status online"

    if job_id:
        job = frappe.get_value(
            "Job Card",
            job_id,
            ["name", "status", "device_type"],
            as_dict=True
        )

        if not job:
            context.error = "Invalid Job ID"

        context.job = job