frappe.ready(function() {
    if (frappe.boot.quickfix_shop_name) {
        $(".navbar-brand").append(
            `<span style="margin-left:10px;font-weight:bold;">
                ${frappe.boot.quickfix_shop_name}
            </span>`
        );
    }
});