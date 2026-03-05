frappe.ui.form.on("Job Card", {

    refresh: function(frm) {

        if (!frappe.user.has_role("QF Manager")) {
            frm.set_df_property("customer_phone", "hidden", 1);
        }

    }

});