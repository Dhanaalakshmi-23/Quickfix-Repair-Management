# Copyright (c) 2026, DhanaaLakshmi
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.tests import IntegrationTestCase


# ---------------------------------------------------------
# FACTORY FUNCTIONS (Reusable test data creators)
# ---------------------------------------------------------

def create_device_type(name="Mobile"):
    """Factory for Device Type"""
    if not frappe.db.exists("Device Type", name):
        return frappe.get_doc({
            "doctype": "Device Type",
            "device_type_name": name
        }).insert()

    return frappe.get_doc("Device Type", name)


def create_technician(name="Test Technician"):
    """Factory for Technician"""
    if not frappe.db.exists("Technician", name):
        return frappe.get_doc({
            "doctype": "Technician",
            "technician_name": name,
            "phone": "9876543210"
        }).insert()

    return frappe.get_doc("Technician", name)


def create_spare_part(name="Screen", unit_cost=100, selling_price=150, stock_qty=10):
    """Factory for Spare Part with configurable stock"""

    if not frappe.db.exists("Spare Part", name):
        return frappe.get_doc({
            "doctype": "Spare Part",
            "part_name": name,
            "unit_cost": unit_cost,
            "selling_price": selling_price,
            "stock_qty": stock_qty
        }).insert()

    return frappe.get_doc("Spare Part", name)


def create_job_card(**kwargs):

    device = create_device_type()
    technician = create_technician()
    part = create_spare_part()

    data = {
        "doctype": "Job Card",
        "customer_name": "Test Customer",
        "customer_phone": "9876543210",
        "device_type": device.name,
        "device_model": "Samsung A10",
        "problem_description": "Screen not working",
        "status": "Received",
        "estimated_cost": 100,
        "technician": technician.name,
        "parts": [
            {
                "spare_part": part.name,
                "quantity": 1,
                "unit_price": part.selling_price
            }
        ]
    }

    for key, value in kwargs.items():
        data[key] = value

    doc = frappe.get_doc(data)
    doc.insert()

    return doc


# ---------------------------------------------------------
# INTEGRATION TESTS
# ---------------------------------------------------------

class IntegrationTestJobCard(IntegrationTestCase):
    """
    Integration tests verify interaction between
    multiple framework components.
    """

    def test_core_validation_still_runs(self):
        """
        If super().validate() is removed in CustomJobCard,
        this test will fail.

        Missing customer_phone should trigger validation error.
        """

        job = frappe.get_doc({
            "doctype": "Job Card",
            "customer_name": "Test Customer",
            "status": "Draft"
        })

        self.assertRaises(
            frappe.ValidationError,
            job.insert
        )


# ---------------------------------------------------------
# UNIT TESTS
# ---------------------------------------------------------

class TestJobCard(FrappeTestCase):

    def setUp(self):
        """
        setUp runs before each test.

        FrappeTestCase wraps each test inside a database
        transaction.

        After the test finishes, Frappe automatically performs
        a database ROLLBACK.

        This means:
        • Any documents created during the test are removed
        • Database returns to its original clean state
        • tearDown() cleanup is unnecessary

        The rollback happens immediately after each test method.
        """

        self.device = create_device_type()
        self.technician = create_technician()
        self.part = create_spare_part()

    # -----------------------------------------------------

    def test_happy_path_insert(self):
        """A fully valid Job Card should save without errors."""

        doc = create_job_card()

        self.assertTrue(frappe.db.exists("Job Card", doc.name))
        self.assertEqual(doc.docstatus, 0)

    # -----------------------------------------------------

    def test_phone_validation(self):
        """Phone number must be exactly 10 numeric digits."""

        # too short
        with self.assertRaises(frappe.ValidationError):
            create_job_card(customer_phone="12345")

        # too long
        with self.assertRaises(frappe.ValidationError):
            create_job_card(customer_phone="123456789012")

        # contains letters
        with self.assertRaises(frappe.ValidationError):
            create_job_card(customer_phone="abcd123456")

        # valid phone
        doc = create_job_card(customer_phone="9876543210")
        self.assertTrue(doc.name)

    # -----------------------------------------------------

    def test_spare_part_price_validation(self):
        """Selling price must be greater than cost."""

        # equal price
        with self.assertRaises(frappe.ValidationError):
            create_spare_part("Battery1", 100, 100)

        # less price
        with self.assertRaises(frappe.ValidationError):
            create_spare_part("Battery2", 100, 90)

        # valid case
        doc = create_spare_part("Battery3", 100, 101)
        self.assertTrue(doc.name)

    # -----------------------------------------------------

    def test_final_amount_computation(self):
        """
        Ensure parts_total and final_amount
        are computed correctly.
        """

        part = create_spare_part("Camera", 100, 200)

        job = create_job_card(parts=[
            {
                "spare_part": part.name,
                "quantity": 2,
                "unit_price": 200
            }
        ])

        expected_parts_total = 400

        settings = frappe.get_single("QuickFix Settings")
        labour_charge = settings.default_labour_charge

        self.assertEqual(job.parts_total, expected_parts_total)
        self.assertEqual(job.final_amount, expected_parts_total + labour_charge)

    # -----------------------------------------------------

    def test_status_transition_guard(self):
        """
        Technician must be assigned
        before status becomes 'In Repair'.
        """

        with self.assertRaises(frappe.ValidationError):
            create_job_card(status="In Repair", technician=None)

        technician = create_technician()

        doc = create_job_card(
            status="In Repair",
            technician=technician.name
        )

        self.assertTrue(doc.name)

    # -----------------------------------------------------

    def test_estimated_cost_required(self):
        """
        estimated_cost must be provided
        when status is 'In Repair'.
        """

        with self.assertRaises(frappe.ValidationError):
            create_job_card(status="In Repair", estimated_cost=0)

    # -----------------------------------------------------

    def test_child_table_computation(self):
        """
        Each child row total_price must equal
        quantity * unit_price.
        """

        part1 = create_spare_part("Speaker", 100, 200)
        part2 = create_spare_part("Mic", 50, 100)

        job = create_job_card(parts=[
            {
                "spare_part": part1.name,
                "quantity": 2,
                "unit_price": 200
            },
            {
                "spare_part": part2.name,
                "quantity": 3,
                "unit_price": 100
            }
        ])

        row1 = job.parts[0]
        row2 = job.parts[1]

        self.assertEqual(row1.total_price, 400)
        self.assertEqual(row2.total_price, 300)

        self.assertEqual(job.parts_total, 700)
        
