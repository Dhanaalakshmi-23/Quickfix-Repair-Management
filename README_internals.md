### C1 - Child Table Internals
Q1 : Automatic Columns: When a row is appended to a child table and saved, Frappe automatically populates four key system columns to maintain the relationship and order: 
1.parent
2.parentfield
3.parenttype
4.idx

Q2 : The DB table name for the Part Usage Entry DocType is tabPart Usage Entry

Q3 : If a row at idx=2 is deleted and the parent document is re-saved, Frappe automatically re-calculates the idx values for all remaining rows to maintain the sequence (continuous series of integers).

### C3 - Renaming Task
Q1 : Link field stores the document name (primary key) of the linked document. The renamed document will update automatically because frappe maintains link integrity at database level.
Track Changes means:
Frappe stores modification history of field values. Changes are visible in the document timeline. We can see the Old value, New value, Who changed it, When it was changed

Q2 : Unique - Database level unique index is created when we set setting unique for a feild. Even if we skip the validations the DB will reject duplicates.

    frappe.db.exists() - Checks manually before saving the document and it is application-level validation. It can be bypassed if logic is removed.