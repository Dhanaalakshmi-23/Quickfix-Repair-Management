frappe.query_reports["Technician Performance Report"] = {

    "filters": [

        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },

        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        },

        {
            "fieldname": "technician",
            "label": "Technician",
            "fieldtype": "Link",
            "options": "Technician"
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname == "completion_rate" && data) {

            if (data.completion_rate < 70) {
                value = "<span style='color:red;font-weight:bold'>" + value + "</span>";
            }

            if (data.completion_rate >= 90) {
                value = "<span style='color:green;font-weight:bold'>" + value + "</span>";
            }

        }

        return value;
    }
};