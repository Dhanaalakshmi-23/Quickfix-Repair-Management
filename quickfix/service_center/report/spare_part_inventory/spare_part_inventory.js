// Copyright (c) 2026, DhanaaLakshmi and contributors
// For license information, please see license.txt


frappe.query_reports["Spare Part Inventory"] = {
    "filters": [],

    formatter: function(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (data && data.stock_qty !== undefined && data.reorder_level !== undefined) {

            if (data.stock_qty <= data.reorder_level) {
                //value = `<span style="background-color:#ffcccc;">${value}</span>`;
                value = `<span style="color: red; font-weight: bold;">${value}</span>`;
            }

        }

        return value;
    }
};
// frappe.query_reports["Spare Parts Inventory"] = {
//   "filters": [],
//   formatter: function(value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);

//         // Red background for rows where stock_qty <= reorder_level
//         if (data && data.stock_qty !== undefined && data.reorder_level !== undefined) {
//             if (data.stock_qty <= data.reorder_level) {
//                 value = <span style="color: red; font-weight: bold;">${value}</span>;
//             }
//         }

//         return value;
//     }
// };
