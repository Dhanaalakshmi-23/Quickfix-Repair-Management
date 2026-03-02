// Copyright (c) 2026, DhanaaLakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {

    setup: function(frm) {

        frm.set_query("assigned_technician", function() {
            return {
                filters: {
                    status: "Active",
                    specialization: frm.doc.device_type
                }
            };
        });

    },

    onload: function(frm) {

        frappe.realtime.on("job_ready", function(data) {
            if (data.name === frm.doc.name) {
                frappe.show_alert({
                    message: "This Job is Ready!",
                    indicator: "green"
                });
            }
        });

    },

    refresh: function(frm) {

        if (frm.doc.status === "Open") {
            frm.dashboard.add_indicator("Open", "orange");
        }
        else if (frm.doc.status === "In Progress") {
            frm.dashboard.add_indicator("In Progress", "blue");
        }
        else if (frm.doc.status === "Ready for Delivery") {
            frm.dashboard.add_indicator("Ready", "green");
        }

        if (frm.doc.status === "Ready for Delivery" && frm.doc.docstatus === 1) {

            frm.add_custom_button("Mark as Delivered", function() {

                frappe.call({
                    method: "quickfix.api.mark_delivered",
                    args: {
                        job_card: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frm.reload_doc();
                        }
                    }
                });

            });
        }

        if (frappe.boot.quickfix_shop_name) {
            frm.page.set_indicator(
                frappe.boot.quickfix_shop_name,
                "blue"
            );
        }



    },

    assigned_technician: function(frm) {

        if (!frm.doc.assigned_technician) return;

        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Technician",
                filters: { name: frm.doc.assigned_technician },
                fieldname: "specialization"
            },
            callback: function(r) {

                if (r.message) {

                    let tech_spec = r.message.specialization;

                    if (tech_spec !== frm.doc.device_type) {
                        frappe.msgprint(
                            "⚠ Technician specialization does not match device type."
                        );
                    }

                }
            }
        });

    },

});
frappe.ui.form.on("Part Usage Entry", {

    quantity: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        if (row.quantity && row.unit_price) {

            let total = row.quantity * row.unit_price;

            frappe.model.set_value(
                cdt,
                cdn,
                "total_price",
                total
            );
        }

    }

});
