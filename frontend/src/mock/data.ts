import type { Application, ApplicationSummary, DashboardStats, AgentResponse } from '../types';

// ─── Mock Applications ───

export const mockApplications: Application[] = [
  {
    application_id: 'APP-0001',
    applicant_name: 'Rahul Kumar',
    applicant_email: 'rahul.kumar@email.com',
    loan_type: 'Home Loan',
    status: 'review',
    created_at: '2026-09-10T10:30:00Z',
    updated_at: '2026-09-11T08:15:00Z',
    documents: [
      {
        document_id: 'DOC-001',
        file_name: 'payslip_march2026.pdf',
        type: 'payslip',
        status: 'completed',
        pages: 2,
        ocr_confidence: 94,
        file_size: 245000,
        uploaded_at: '2026-09-10T10:31:00Z',
        fields: [
          { field_name: 'Employee Name', value: 'Rahul Kumar', confidence: 97, page: 1 },
          { field_name: 'Employer', value: 'Horizon Technologies Pvt. Ltd.', confidence: 95, page: 1 },
          { field_name: 'Pay Period', value: 'March 2026', confidence: 98, page: 1 },
          { field_name: 'Gross Salary', value: '₹80,000', confidence: 93, page: 1 },
          { field_name: 'Net Salary', value: '₹72,000', confidence: 93, page: 1 },
          { field_name: 'Employee ID', value: 'HT-2847', confidence: 96, page: 1 },
          { field_name: 'PAN', value: 'ABCPK1234F', confidence: 91, page: 2 },
        ],
      },
      {
        document_id: 'DOC-002',
        file_name: 'bank_statement_q1_2026.pdf',
        type: 'bank_statement',
        status: 'completed',
        pages: 4,
        ocr_confidence: 91,
        file_size: 512000,
        uploaded_at: '2026-09-10T10:32:00Z',
        fields: [
          { field_name: 'Account Holder', value: 'Rahul Kumar', confidence: 96, page: 1 },
          { field_name: 'Bank', value: 'State Bank of India', confidence: 98, page: 1 },
          { field_name: 'Account Number', value: 'XXXX-XXXX-4521', confidence: 94, page: 1 },
          { field_name: 'Average Monthly Balance', value: '₹2,45,000', confidence: 89, page: 3 },
          { field_name: 'Monthly Credit (Avg)', value: '₹74,167', confidence: 88, page: 4 },
        ],
      },
      {
        document_id: 'DOC-003',
        file_name: 'itr_2025_26.pdf',
        type: 'tax_return',
        status: 'completed',
        pages: 6,
        ocr_confidence: 88,
        file_size: 890000,
        uploaded_at: '2026-09-10T10:33:00Z',
        fields: [
          { field_name: 'Assessee Name', value: 'Rahul Kumar', confidence: 95, page: 1 },
          { field_name: 'PAN', value: 'ABCPK1234F', confidence: 97, page: 1 },
          { field_name: 'Assessment Year', value: '2025-26', confidence: 99, page: 1 },
          { field_name: 'Total Income', value: '₹7,80,000', confidence: 92, page: 2 },
          { field_name: 'Tax Paid', value: '₹52,000', confidence: 90, page: 3 },
        ],
      },
      {
        document_id: 'DOC-004',
        file_name: 'aadhaar_card.pdf',
        type: 'id_proof',
        status: 'completed',
        pages: 1,
        ocr_confidence: 96,
        file_size: 180000,
        uploaded_at: '2026-09-10T10:34:00Z',
        fields: [
          { field_name: 'Name', value: 'Rahul Kumar', confidence: 98, page: 1 },
          { field_name: 'Aadhaar Number', value: 'XXXX-XXXX-7890', confidence: 97, page: 1 },
          { field_name: 'Address', value: '42, MG Road, Bengaluru, Karnataka - 560001', confidence: 91, page: 1 },
          { field_name: 'Date of Birth', value: '15-06-1992', confidence: 96, page: 1 },
        ],
      },
    ],
    verification: {
      matches: [
        {
          field_name: 'Name',
          values: [
            { document: 'Payslip', value: 'Rahul Kumar' },
            { document: 'Bank Statement', value: 'Rahul Kumar' },
            { document: 'Tax Return', value: 'Rahul Kumar' },
            { document: 'ID Proof', value: 'Rahul Kumar' },
          ],
          status: 'PASS',
        },
        {
          field_name: 'PAN',
          values: [
            { document: 'Payslip', value: 'ABCPK1234F' },
            { document: 'Tax Return', value: 'ABCPK1234F' },
          ],
          status: 'PASS',
        },
        {
          field_name: 'Address',
          values: [
            { document: 'ID Proof', value: '42, MG Road, Bengaluru' },
          ],
          status: 'PASS',
        },
      ],
      mismatches: [
        {
          field_name: 'Annual Income',
          values: [
            { document: 'Payslip', value: '₹9,60,000 (annualized)' },
            { document: 'Bank Statement', value: '₹8,90,000 (annualized credits)' },
            { document: 'Tax Return', value: '₹7,80,000' },
          ],
          status: 'MISMATCH',
        },
      ],
      missing_documents: ['Address Proof'],
    },
    risk: {
      score: 62,
      level: 'MEDIUM',
      flags: [
        {
          id: 'FLAG-001',
          severity: 'HIGH',
          reason: 'Income Discrepancy Across Documents',
          details: 'The annualized income from the payslip (₹9,60,000) differs significantly from the income declared in the tax return (₹7,80,000). The difference of ₹1,80,000 exceeds the 10% threshold.',
          evidence: [
            { document: 'payslip_march2026.pdf', page: 1, value: '₹80,000/month → ₹9,60,000/year' },
            { document: 'itr_2025_26.pdf', page: 2, value: '₹7,80,000 total income' },
          ],
        },
        {
          id: 'FLAG-002',
          severity: 'MEDIUM',
          reason: 'Bank Credits Below Payslip Net Salary',
          details: 'Average monthly bank credits (₹74,167) are lower than the stated net salary (₹72,000). While close, this warrants verification of additional deductions or accounts.',
          evidence: [
            { document: 'bank_statement_q1_2026.pdf', page: 4, value: '₹74,167 avg monthly credit' },
            { document: 'payslip_march2026.pdf', page: 1, value: '₹72,000 net salary' },
          ],
        },
        {
          id: 'FLAG-003',
          severity: 'LOW',
          reason: 'Address Proof Document Missing',
          details: 'Separate address proof document has not been provided. Address is available on Aadhaar card but a standalone utility bill or rental agreement may be required per policy.',
          evidence: [],
        },
      ],
    },
    recommendation: 'NEEDS_HUMAN_REVIEW',
  },
  {
    application_id: 'APP-0002',
    applicant_name: 'Priya Sharma',
    applicant_email: 'priya.sharma@email.com',
    loan_type: 'Personal Loan',
    status: 'completed',
    created_at: '2026-09-09T14:20:00Z',
    updated_at: '2026-09-10T16:45:00Z',
    documents: [
      {
        document_id: 'DOC-005',
        file_name: 'salary_slip_aug2026.pdf',
        type: 'payslip',
        status: 'completed',
        pages: 1,
        ocr_confidence: 96,
        file_size: 198000,
        uploaded_at: '2026-09-09T14:21:00Z',
        fields: [
          { field_name: 'Employee Name', value: 'Priya Sharma', confidence: 98, page: 1 },
          { field_name: 'Employer', value: 'Infosys Ltd.', confidence: 97, page: 1 },
          { field_name: 'Gross Salary', value: '₹1,20,000', confidence: 95, page: 1 },
          { field_name: 'Net Salary', value: '₹1,02,000', confidence: 95, page: 1 },
        ],
      },
      {
        document_id: 'DOC-006',
        file_name: 'bank_statement_priya.pdf',
        type: 'bank_statement',
        status: 'completed',
        pages: 3,
        ocr_confidence: 93,
        file_size: 420000,
        uploaded_at: '2026-09-09T14:22:00Z',
        fields: [
          { field_name: 'Account Holder', value: 'Priya Sharma', confidence: 97, page: 1 },
          { field_name: 'Bank', value: 'HDFC Bank', confidence: 98, page: 1 },
          { field_name: 'Monthly Credit (Avg)', value: '₹1,03,500', confidence: 91, page: 3 },
        ],
      },
      {
        document_id: 'DOC-007',
        file_name: 'itr_priya.pdf',
        type: 'tax_return',
        status: 'completed',
        pages: 5,
        ocr_confidence: 90,
        file_size: 780000,
        uploaded_at: '2026-09-09T14:23:00Z',
        fields: [
          { field_name: 'Assessee Name', value: 'Priya Sharma', confidence: 96, page: 1 },
          { field_name: 'Total Income', value: '₹14,20,000', confidence: 93, page: 2 },
        ],
      },
      {
        document_id: 'DOC-008',
        file_name: 'pan_card_priya.pdf',
        type: 'id_proof',
        status: 'completed',
        pages: 1,
        ocr_confidence: 97,
        file_size: 145000,
        uploaded_at: '2026-09-09T14:24:00Z',
        fields: [
          { field_name: 'Name', value: 'Priya Sharma', confidence: 99, page: 1 },
          { field_name: 'PAN', value: 'BGHPS5678K', confidence: 98, page: 1 },
        ],
      },
      {
        document_id: 'DOC-009',
        file_name: 'electricity_bill.pdf',
        type: 'address_proof',
        status: 'completed',
        pages: 1,
        ocr_confidence: 89,
        file_size: 210000,
        uploaded_at: '2026-09-09T14:25:00Z',
        fields: [
          { field_name: 'Name', value: 'Priya Sharma', confidence: 90, page: 1 },
          { field_name: 'Address', value: '15, Jubilee Hills, Hyderabad - 500033', confidence: 87, page: 1 },
        ],
      },
    ],
    verification: {
      matches: [
        {
          field_name: 'Name',
          values: [
            { document: 'Payslip', value: 'Priya Sharma' },
            { document: 'Bank Statement', value: 'Priya Sharma' },
            { document: 'Tax Return', value: 'Priya Sharma' },
            { document: 'ID Proof', value: 'Priya Sharma' },
            { document: 'Address Proof', value: 'Priya Sharma' },
          ],
          status: 'PASS',
        },
        {
          field_name: 'Annual Income',
          values: [
            { document: 'Payslip', value: '₹14,40,000 (annualized)' },
            { document: 'Tax Return', value: '₹14,20,000' },
          ],
          status: 'PASS',
        },
      ],
      mismatches: [],
      missing_documents: [],
    },
    risk: {
      score: 18,
      level: 'LOW',
      flags: [
        {
          id: 'FLAG-004',
          severity: 'PASS',
          reason: 'All Documents Verified Successfully',
          details: 'All submitted documents have been verified. Name, income, and address information is consistent across all documents.',
          evidence: [],
        },
      ],
    },
    recommendation: 'APPROVE',
  },
  {
    application_id: 'APP-0003',
    applicant_name: 'Amit Patel',
    applicant_email: 'amit.patel@email.com',
    loan_type: 'Business Loan',
    status: 'processing',
    created_at: '2026-09-11T09:00:00Z',
    updated_at: '2026-09-11T09:15:00Z',
    documents: [
      {
        document_id: 'DOC-010',
        file_name: 'gst_return.pdf',
        type: 'tax_return',
        status: 'processing',
        pages: 8,
        ocr_confidence: 0,
        file_size: 1200000,
        uploaded_at: '2026-09-11T09:01:00Z',
        fields: [],
      },
      {
        document_id: 'DOC-011',
        file_name: 'business_bank_stmt.pdf',
        type: 'bank_statement',
        status: 'completed',
        pages: 6,
        ocr_confidence: 87,
        file_size: 950000,
        uploaded_at: '2026-09-11T09:02:00Z',
        fields: [
          { field_name: 'Account Holder', value: 'Amit Patel (Patel Enterprises)', confidence: 92, page: 1 },
          { field_name: 'Bank', value: 'ICICI Bank', confidence: 97, page: 1 },
        ],
      },
    ],
    verification: { matches: [], mismatches: [], missing_documents: ['Payslip', 'ID Proof', 'Address Proof'] },
    risk: { score: 0, level: 'MEDIUM', flags: [] },
    recommendation: 'INSUFFICIENT_DATA',
  },
  {
    application_id: 'APP-0004',
    applicant_name: 'Sneha Reddy',
    applicant_email: 'sneha.r@email.com',
    loan_type: 'Home Loan',
    status: 'review',
    created_at: '2026-09-08T11:00:00Z',
    updated_at: '2026-09-11T07:30:00Z',
    documents: [
      {
        document_id: 'DOC-012',
        file_name: 'payslip_sneha.pdf',
        type: 'payslip',
        status: 'completed',
        pages: 2,
        ocr_confidence: 95,
        file_size: 260000,
        uploaded_at: '2026-09-08T11:01:00Z',
        fields: [
          { field_name: 'Employee Name', value: 'Sneha Reddy', confidence: 97, page: 1 },
          { field_name: 'Employer', value: 'TCS', confidence: 98, page: 1 },
          { field_name: 'Net Salary', value: '₹95,000', confidence: 94, page: 1 },
        ],
      },
      {
        document_id: 'DOC-013',
        file_name: 'bank_stmt_sneha.pdf',
        type: 'bank_statement',
        status: 'completed',
        pages: 4,
        ocr_confidence: 92,
        file_size: 540000,
        uploaded_at: '2026-09-08T11:02:00Z',
        fields: [
          { field_name: 'Account Holder', value: 'Sneha Reddy', confidence: 96, page: 1 },
          { field_name: 'Monthly Credit (Avg)', value: '₹96,200', confidence: 90, page: 4 },
        ],
      },
      {
        document_id: 'DOC-014',
        file_name: 'itr_sneha.pdf',
        type: 'tax_return',
        status: 'completed',
        pages: 5,
        ocr_confidence: 91,
        file_size: 720000,
        uploaded_at: '2026-09-08T11:03:00Z',
        fields: [
          { field_name: 'Assessee Name', value: 'S. Reddy', confidence: 88, page: 1 },
          { field_name: 'Total Income', value: '₹11,40,000', confidence: 92, page: 2 },
        ],
      },
    ],
    verification: {
      matches: [
        {
          field_name: 'Annual Income',
          values: [
            { document: 'Payslip', value: '₹11,40,000 (annualized)' },
            { document: 'Tax Return', value: '₹11,40,000' },
          ],
          status: 'PASS',
        },
      ],
      mismatches: [
        {
          field_name: 'Name',
          values: [
            { document: 'Payslip', value: 'Sneha Reddy' },
            { document: 'Bank Statement', value: 'Sneha Reddy' },
            { document: 'Tax Return', value: 'S. Reddy' },
          ],
          status: 'MISMATCH',
        },
      ],
      missing_documents: ['ID Proof', 'Address Proof'],
    },
    risk: {
      score: 45,
      level: 'MEDIUM',
      flags: [
        {
          id: 'FLAG-005',
          severity: 'MEDIUM',
          reason: 'Name Variation Across Documents',
          details: 'Tax return shows abbreviated name "S. Reddy" while other documents show "Sneha Reddy". This may be a data entry issue but requires verification.',
          evidence: [
            { document: 'itr_sneha.pdf', page: 1, value: 'S. Reddy' },
            { document: 'payslip_sneha.pdf', page: 1, value: 'Sneha Reddy' },
          ],
        },
        {
          id: 'FLAG-006',
          severity: 'MEDIUM',
          reason: 'Missing Identity & Address Documents',
          details: 'ID Proof and Address Proof documents have not been submitted. These are required for complete verification.',
          evidence: [],
        },
      ],
    },
    recommendation: 'NEEDS_HUMAN_REVIEW',
  },
  {
    application_id: 'APP-0005',
    applicant_name: 'Vikram Singh',
    applicant_email: 'vikram.singh@email.com',
    loan_type: 'Vehicle Loan',
    status: 'completed',
    created_at: '2026-09-07T08:00:00Z',
    updated_at: '2026-09-08T14:00:00Z',
    documents: [
      {
        document_id: 'DOC-015',
        file_name: 'payslip_vikram.pdf',
        type: 'payslip',
        status: 'completed',
        pages: 1,
        ocr_confidence: 97,
        file_size: 190000,
        uploaded_at: '2026-09-07T08:01:00Z',
        fields: [
          { field_name: 'Employee Name', value: 'Vikram Singh', confidence: 99, page: 1 },
          { field_name: 'Net Salary', value: '₹65,000', confidence: 96, page: 1 },
        ],
      },
      {
        document_id: 'DOC-016',
        file_name: 'bank_stmt_vikram.pdf',
        type: 'bank_statement',
        status: 'completed',
        pages: 3,
        ocr_confidence: 94,
        file_size: 380000,
        uploaded_at: '2026-09-07T08:02:00Z',
        fields: [
          { field_name: 'Account Holder', value: 'Vikram Singh', confidence: 98, page: 1 },
          { field_name: 'Monthly Credit (Avg)', value: '₹66,000', confidence: 93, page: 3 },
        ],
      },
    ],
    verification: {
      matches: [
        {
          field_name: 'Name',
          values: [
            { document: 'Payslip', value: 'Vikram Singh' },
            { document: 'Bank Statement', value: 'Vikram Singh' },
          ],
          status: 'PASS',
        },
      ],
      mismatches: [],
      missing_documents: [],
    },
    risk: { score: 12, level: 'LOW', flags: [] },
    recommendation: 'APPROVE',
  },
];

// ─── Helper to derive summary from full application ───

export function toSummary(app: Application): ApplicationSummary {
  return {
    application_id: app.application_id,
    applicant_name: app.applicant_name,
    status: app.status,
    document_count: app.documents.filter(d => d.status === 'completed').length,
    total_documents: app.documents.length,
    risk_level: app.risk.level,
    updated_at: app.updated_at,
  };
}

// ─── Dashboard Stats ───

export function getMockStats(): DashboardStats {
  return {
    total: mockApplications.length,
    pending: mockApplications.filter(a => a.status === 'processing').length,
    needs_attention: mockApplications.filter(a => a.status === 'review').length,
    completed: mockApplications.filter(a => a.status === 'completed').length,
  };
}

// ─── Mock Chat Responses ───

export function getMockAgentResponse(query: string): AgentResponse {
  const q = query.toLowerCase();

  if (q.includes('flag') || q.includes('why')) {
    return {
      response: 'This application was flagged primarily due to an income discrepancy across documents. The annualized payslip income (₹9,60,000) differs from the tax return declared income (₹7,80,000) by ₹1,80,000, which exceeds the 10% variance threshold. Additionally, a separate address proof document is missing from the submission.',
      sources: [
        { document: 'payslip_march2026.pdf', page: 1 },
        { document: 'itr_2025_26.pdf', page: 2 },
      ],
    };
  }

  if (q.includes('missing') || q.includes('document')) {
    return {
      response: 'The application is currently missing an Address Proof document. While the applicant\'s address is available on the Aadhaar card, a standalone address verification document (such as a utility bill or rental agreement) may be required per lending policy. I recommend requesting this document from the applicant.',
      sources: [],
    };
  }

  if (q.includes('income') || q.includes('mismatch') || q.includes('inconsisten')) {
    return {
      response: 'There is a significant income inconsistency detected:\n\n• **Payslip**: ₹80,000/month → ₹9,60,000/year (annualized)\n• **Bank Statement**: ₹74,167/month average credits → ₹8,90,000/year\n• **Tax Return**: ₹7,80,000 declared total income\n\nThe difference between the payslip annualized income and tax return is ₹1,80,000 (18.75% variance). This could indicate under-reporting of income in the tax return, or the payslip may include recent salary revisions not yet reflected in the ITR.',
      sources: [
        { document: 'payslip_march2026.pdf', page: 1 },
        { document: 'bank_statement_q1_2026.pdf', page: 4 },
        { document: 'itr_2025_26.pdf', page: 2 },
      ],
    };
  }

  if (q.includes('recommend') || q.includes('approv') || q.includes('decision')) {
    return {
      response: 'Based on the analysis, this application has been recommended for **Human Review**. The system does not automatically approve or reject applications. Key factors for your consideration:\n\n1. Income discrepancy of 18.75% between payslip and tax return\n2. Missing address proof document\n3. All name and PAN verifications passed\n4. Bank credits are consistent with stated salary\n\nThe final lending decision rests with you as the reviewing officer.',
      sources: [],
    };
  }

  return {
    response: 'I can help you with information about this loan application. You can ask me about:\n\n• Why the application was flagged\n• Income discrepancies or mismatches\n• Missing documents\n• Verification results\n• Risk assessment details\n\nWhat would you like to know?',
    sources: [],
  };
}
