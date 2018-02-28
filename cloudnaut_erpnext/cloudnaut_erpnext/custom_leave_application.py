from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.leave_application.leave_application import get_leave_allocation_records
from frappe.utils import get_datetime_str, formatdate, format_datetime, getdate, flt
from collections import defaultdict


def validate_monthly_leaves(doc, method):
	pass
	# monthly_max_holidays = flt(frappe.db.get_value("HR Settings", None, "monthly_max_holidays"))
	# if monthly_max_holidays and doc.leave_type == 'Casual Leave':
	# 	from_month, to_month = getdate(doc.from_date).month, getdate(doc.to_date).month
	# 	if from_month != to_month:
	# 		frappe.throw(_("For leave across two different months, Please create two different leave application."))
	# 	allocated_leaves = get_leave_allocation_records(doc.from_date, doc.employee)
	# 	allocation_period = allocated_leaves.get(doc.employee, {}).get("Casual Leave", {})
	# 	if allocation_period:
	# 		month_wise_leaves = frappe.db.sql(""" select ct.leave_month, sum(ct.total_leave_days) as total_leaves 
	# 			from (select month(from_date) as leave_month, total_leave_days from `tabLeave Application` 
	# 			where from_date between %s and %s and employee = %s and leave_type = 'Casual Leave' 
	# 			and docstatus != 2 and name != %s ) as ct group by leave_month """, (allocation_period.get("from_date").strftime('%Y-%m-%d'), 
	# 			allocation_period.get("to_date").strftime('%Y-%m-%d'), doc.employee, doc.name), as_dict=1)
	# 		total_allowed_leaves = get_allowed_leaves(from_month, allocation_period, month_wise_leaves, monthly_max_holidays)
	# 		if doc.total_leave_days > total_allowed_leaves:
	# 			frappe.throw(_("""Only <b>{0}</b> Casual leaves are allowed for the month of <b>{1}</b>. For extra leaves, Please 
	# 				create leave application with leave type as <b>Leave Without Pay</b>. """.format(total_allowed_leaves, getdate(doc.from_date).strftime("%B"))))


def get_allowed_leaves(current_leave_month, allocation_period, month_wise_leaves, monthly_max_holidays):
	month_leave_dict = defaultdict(float)
	for month in month_wise_leaves:
		month_leave_dict[month.leave_month] = month.total_leaves
	total_leave_month =  current_leave_month - allocation_period.get("from_date").month + 1	
	total_allowed_leaves = total_leave_month * monthly_max_holidays
	month_range = range(allocation_period.get("from_date").month, allocation_period.get("to_date").month + 1)
	for month in month_range:
		if month <= current_leave_month and month_leave_dict[month]:
			total_allowed_leaves -= month_leave_dict[month]
	return total_allowed_leaves


def set_pan_and_tan_nos(doc, method):
	emp_pan_no = frappe.db.get_value("Employee", doc.employee, ["pan_no"])
	comp = frappe.db.get_value("Company", doc.company, ["company_pan_no", "company_tan_no"], as_dict=True)
	doc.company_tan_no = comp.get("company_tan_no", "")
	doc.company_pan_no = comp.get("company_pan_no", "")
	doc.employee_pan_no = emp_pan_no