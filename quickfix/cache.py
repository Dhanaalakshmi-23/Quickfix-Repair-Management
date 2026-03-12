import frappe

def clear_job_card_cache(doc, method):

    cache = frappe.cache()

    cache.delete_value("job_card_status_chart")