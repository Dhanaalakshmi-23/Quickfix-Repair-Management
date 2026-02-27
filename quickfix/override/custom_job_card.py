import frappe
from quickfix.service_center.doctype.job_card.job_card import JobCard

class CustomJobCard(JobCard):
    def validate(self):
        super().validate()
        self.check_urgent_unassigned()
    def check_urgent_unassigned(self):
        if self.priority == "Urgent" and not self.assigned_technician:
            settings = frappe.get_single("QuickFix Settings")
            frappe.enqueue(
                "quickfix.utils.send_urgent_alert",
                job_card=self.name,
                manager=settings.manager_email
            )

"""
Method Resolution Order (MRO) defines the order in which Python looks for
methods in a class hierarchy. Since CustomJobCard inherits from JobCard,
Python first checks CustomJobCard methods, then parent JobCard methods.

Calling super() ensures that the parent class's validate() method executes
before the overridden logic. If super() is not called, the base class
business rules and validations will be skipped, breaking core functionality.
Therefore, calling super() is non-negotiable when overriding lifecycle methods.
"""

"""
override_doctype_class should be used when you want to extend or modify
the core behavior of a DocType using inheritance and object-oriented design.
It is best when you need full control over lifecycle methods and want to
reuse existing logic using super().

doc_events is better for lightweight hooks or when modifying behavior
from another app without changing the class structure. It is event-based
and less tightly coupled than overriding the class.
"""

