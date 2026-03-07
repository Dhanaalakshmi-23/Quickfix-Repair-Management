import frappe

def execute(filters=None):

    columns = get_columns()
    data = get_data()

    total_parts = len(data)
    below_reorder = 0
    total_inventory_value = 0
    total_stock = 0

    for row in data:
        if row["stock_qty"] <= row["reorder_level"]:
            below_reorder += 1

        total_inventory_value += row["stock_qty"] * row["unit_cost"]
        total_stock += row["stock_qty"]
        

    report_summary = [
        {
            "label": "Total Parts",
            "value": total_parts,
            "indicator": "Blue"
        },
        {
            "label": "Below Reorder",
            "value": below_reorder,
            "indicator": "Red"
        },
        {
            "label": "Total Inventory Value",
            "value": total_inventory_value,
            "indicator": "Green"
        }
    ]

    data.append({
        "part_name": "TOTAL",
        "stock_qty": total_stock,
        "inventory_value": total_inventory_value
    })

    return columns, data, None, None, report_summary


def get_columns():

    return [
        {"label": "Part Name", "fieldname": "part_name", "fieldtype": "Data", "width": 150},
        {"label": "Part Code", "fieldname": "part_code", "fieldtype": "Data", "width": 120},
        {"label": "Device Type", "fieldname": "compatible_device_type", "fieldtype": "Link", "options": "Device Type", "width": 150},
        {"label": "Stock Qty", "fieldname": "stock_qty", "fieldtype": "Float", "width": 120},
        {"label": "Reorder Level", "fieldname": "reorder_level", "fieldtype": "Float", "width": 120},
        {"label": "Unit Cost", "fieldname": "unit_cost", "fieldtype": "Currency", "width": 120},
        {"label": "Selling Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 120},
        {"label": "Margin %", "fieldname": "margin", "fieldtype": "Percent", "width": 120}
    ]


def get_data():

    parts = frappe.get_all(
        "Spare Part",
        fields=[
            "part_name",
            "part_code",
            "compatible_device_type",
            "stock_qty",
            "reorder_level",
            "unit_cost",
            "selling_price"
        ]
    )

    data = []

    for p in parts:

        margin = 0

        if p.unit_cost:
            margin = ((p.selling_price - p.unit_cost) / p.unit_cost) * 100

        data.append({
            "part_name": p.part_name,
            "part_code": p.part_code,
            "compatible_device_type": p.compatible_device_type,
            "stock_qty": p.stock_qty,
            "reorder_level": p.reorder_level,
            "unit_cost": p.unit_cost,
            "selling_price": p.selling_price,
            "margin": margin
        })

    return data