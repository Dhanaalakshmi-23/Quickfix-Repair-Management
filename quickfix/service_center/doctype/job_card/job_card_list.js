frappe.listview_settings["Job Card"] = {

    // Fetch extra fields
    add_fields: ["final_amount", "priority", "status"],
    has_indicator_for_draft: true,
    get_indicator: function(doc) {

        if (doc.status === "Draft") {
            return ["Draft", "orange", "status,=,Draft"];
        }

        if (doc.status === "In Repair") {
            return ["In Repair", "blue", "status,=,In Repair"];
        }

        if (doc.status === "Ready for Delivery") {
            return ["Ready", "green", "status,=,Ready for Delivery"];
        }

        if (doc.status === "Rejected") {
            return ["Rejected", "red", "status,=,Rejected"];
        }

    },

    formatters: {

        final_amount(value) {
            if (!value) return "";
            return "₹ " + value;
        },

        priority(value) {
            if (value === "High") {
                return "<span style='color:red;font-weight:bold'>" + value + "</span>";
            }
            return value;
        }

    },

    button: {

        show: function(doc) {
            return doc.status === "In Repair";
        },

        get_label: function() {
            return "Complete Repair";
        },

        get_description: function(doc) {
            return "Mark " + doc.name + " as Ready";
        },

        action: function(doc) {

            frappe.call({
                method: "quickfix.api.mark_ready",
                args: {
                    job_card: doc.name
                },
                callback: function() {
                    frappe.show_alert("Marked as Ready!");
                    frappe.listview.refresh();
                }
            });

        }

    }

};