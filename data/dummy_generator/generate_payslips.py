"""
Dummy Payslip Generator
====================================
Generates realistic payslip PDFs using Faker + Kaggle dataset rows.


TODO: implement payslip PDF generation using Jinja2 templates + ReportLab
"""

# Fields to generate:
#   employee_name, employer, employee_id, pay_period, designation,
#   gross_salary, basic_salary, hra, other_allowances,
#   pf_deduction, tax_deduction, total_deductions, net_salary

# Steps:
#   1. Load a row from Kaggle CSV (income_annum → monthly = income_annum / 12)
#   2. Use Faker for: name, company, address, employee ID
#   3. Calculate salary breakdown (basic=40%, HRA=20%, allowances=40%)
#   4. Render HTML template with Jinja2
#   5. Convert HTML to PDF
