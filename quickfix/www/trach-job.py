import frappe

def get_context(context):

    job_id = frappe.form_dict.get("job_id")

    context.title = "Track Repair Job"
    context.description = "Track your device repair status online"
    context.og_title = "Track Repair Job"

    if job_id:

        job = frappe.get_value(
            "Job Card",
            job_id,
            ["name","status","device_name","modified"],
            as_dict=True
        )

        context.job = job