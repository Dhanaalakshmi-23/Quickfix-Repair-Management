### C1 - Child Table Internals
Q1 : Automatic Columns: When a row is appended to a child table and saved, Frappe automatically populates four key system columns to maintain the relationship and order: 
1.parent
2.parentfield
3.parenttype
4.idx

Q2 : The DB table name for the Part Usage Entry DocType is tabPart Usage Entry

Q3 : If a row at idx=2 is deleted and the parent document is re-saved, Frappe automatically re-calculates the idx values for all remaining rows to maintain the sequence (continuous series of integers).