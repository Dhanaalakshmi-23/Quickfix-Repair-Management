# Copyright (c) 2026, DhanaaLakshmi and Contributors
# See license.txt

# import frappe
import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestJobCard(IntegrationTestCase):
	"""
	Integration tests for JobCard.
	Use this class for testing interactions between multiple components.
	"""

	def test_core_validation_still_runs(self):
			"""
			If super().validate() is removed in CustomJobCard,
			this test will fail.
			"""

			job = frappe.get_doc({
				"doctype": "Job Card",
				"customer_name": "Test Customer",
				"status": "Draft"
				# intentionally missing customer_phone
			})

			# Expect validation error due to missing customer_phone
			self.assertRaises(
				frappe.ValidationError,
				job.insert
			)
