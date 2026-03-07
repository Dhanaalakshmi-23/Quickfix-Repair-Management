frappe.provide("frappe.views")
//  console.log(34567890)
 setTimeout(() =>{
    if (frappe.boot.quickfix_shop_name) {
        let shop_name = frappe.boot.quickfix_shop_name;
        $(".navbar-home").append(
            `<span style="margin-left:10px; font-weight:600;">
                ${shop_name}
            </span>`
        );
    }
},100)
