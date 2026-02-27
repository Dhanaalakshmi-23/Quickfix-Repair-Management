import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SparePart(Document):

    def autoname(self):
        if not self.part_code:
            return

        generated_name = make_autoname("PART-.YYYY.-.####")
        self.name = f"{self.part_code.upper()}-{generated_name}"


    def validate(self):
        self.validate_pricing()


    def validate_pricing(self):

        if self.unit_cost is None or self.selling_price is None:
            return

        if self.selling_price <= self.unit_cost:
            message = (
                f"Selling Price ({self.selling_price}) "
                f"must be greater than Unit Cost ({self.unit_cost})."
            )

            frappe.throw(
                message,
                title="Invalid Pricing"
            )
    
    def autoname(self):
        if self.part_code:
            self.part_code = self.part_code.upper()
        self.name = frappe.model.naming.make_autoname("SP-.####")
        