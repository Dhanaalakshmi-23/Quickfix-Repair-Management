# Copyright (c) 2026, DhanaaLakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime


def execute(filters=None):

    if not filters:
        filters = {}

    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


# -------------------------
# Columns
# -------------------------

def get_columns(filters):

    columns = [

        {
            "label": _("Technician"),
            "fieldname": "technician",
            "fieldtype": "Link",
            "options": "Technician",
            "width": 180
        },

        {
            "label": _("Total Jobs"),
            "fieldname": "total_jobs",
            "fieldtype": "Int",
            "width": 120
        },

        {
            "label": _("Completed"),
            "fieldname": "completed_jobs",
            "fieldtype": "Int",
            "width": 120
        },

        {
            "label": _("Avg Turnaround Days"),
            "fieldname": "avg_turnaround",
            "fieldtype": "Float",
            "width": 150
        },

        {
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 130
        },

        {
            "label": _("Completion Rate %"),
            "fieldname": "completion_rate",
            "fieldtype": "Percent",
            "width": 140
        }
    ]

    # Dynamic Device Type Columns
    device_types = frappe.get_all("Device Type", fields=["name"])

    for dt in device_types:
        fieldname = dt.name.lower().replace(" ", "_")

        columns.append({
            "label": dt.name,
            "fieldname": fieldname,
            "fieldtype": "Int",
            "width": 110
        })

    return columns


# -------------------------
# Data
# -------------------------

def get_data(filters):

    conditions = {}

    if filters.get("technician"):
        conditions["assigned_technician"] = filters.get("technician")

    if filters.get("from_date"):
        conditions["creation"] = [">=", filters.get("from_date")]

    if filters.get("to_date"):
        conditions.setdefault("creation", ["<=", filters.get("to_date")])

    job_cards = frappe.get_list(
        "Job Card",
        fields=[
            "assigned_technician",
            "status",
            "estimated_cost",
            "device_type",
            "creation",
            "modified"
        ],
        filters=conditions,
        limit_page_length=0
    )

    device_types = frappe.get_all("Device Type", fields=["name"])

    technician_data = {}

    for job in job_cards:

        tech = job.assigned_technician

        if not tech:
            continue

        if tech not in technician_data:

            technician_data[tech] = {
                "technician": tech,
                "total_jobs": 0,
                "completed_jobs": 0,
                "revenue": 0,
                "turnaround_total": 0,
                "turnaround_count": 0
            }

            # initialize device counters
            for dt in device_types:
                fieldname = dt.name.lower().replace(" ", "_")
                technician_data[tech][fieldname] = 0

        technician_data[tech]["total_jobs"] += 1

        # Completed Jobs
        if job.status == "Delivered":

            technician_data[tech]["completed_jobs"] += 1

            if job.modified and job.creation:

                diff = job.modified - job.creation
                days = diff.total_seconds() / 86400

                technician_data[tech]["turnaround_total"] += days
                technician_data[tech]["turnaround_count"] += 1

        # Revenue
        technician_data[tech]["revenue"] += job.estimated_cost or 0

        # Device Type Count
        if job.device_type:

            fieldname = job.device_type.lower().replace(" ", "_")

            if fieldname in technician_data[tech]:
                technician_data[tech][fieldname] += 1

    data = []

    for tech in technician_data.values():

        # Avg Turnaround
        if tech["turnaround_count"] > 0:
            avg_turnaround = tech["turnaround_total"] / tech["turnaround_count"]
        else:
            avg_turnaround = 0

        # Completion Rate
        if tech["total_jobs"] > 0:
            completion_rate = (tech["completed_jobs"] / tech["total_jobs"]) * 100
        else:
            completion_rate = 0

        tech["avg_turnaround"] = round(avg_turnaround, 2)
        tech["completion_rate"] = round(completion_rate, 2)

        data.append(tech)

    return data


# -------------------------
# Chart
# -------------------------

def get_chart(data):

    labels = []
    total_jobs = []
    completed_jobs = []

    for row in data:
        labels.append(row["technician"])
        total_jobs.append(row["total_jobs"])
        completed_jobs.append(row["completed_jobs"])

    chart = {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Total Jobs",
                    "values": total_jobs
                },
                {
                    "name": "Delivered Jobs",
                    "values": completed_jobs
                }
            ]
        },
        "type": "bar"
    }

    return chart


# -------------------------
# Report Summary
# -------------------------

def get_summary(data):

    total_jobs = 0
    total_revenue = 0
    best_technician = None
    max_completed = 0

    for row in data:

        total_jobs += row["total_jobs"]
        total_revenue += row["revenue"]

        if row["completed_jobs"] > max_completed:
            max_completed = row["completed_jobs"]
            best_technician = row["technician"]

    summary = [

        {
            "label": "Total Jobs",
            "value": total_jobs,
            "indicator": "Blue"
        },

        {
            "label": "Total Revenue",
            "value": total_revenue,
            "indicator": "Green"
        },

        {
            "label": "Best Technician",
            "value": best_technician or "N/A",
            "indicator": "Orange"
        }
    ]

    return summary