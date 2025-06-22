"use client"

import type { Project, Certificate, Calculations } from "@/lib/types"
import { formatCurrency } from "@/lib/utils"

interface CertificatePDFProps {
  project: Project
  certificate: Certificate
  calculations: Calculations
}

export default function CertificatePDF({ project, certificate, calculations }: CertificatePDFProps) {
  // Format the current date
  const formattedDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  return (
    <div className="font-serif">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold uppercase mb-1">Payment Certificate</h1>
        <p className="text-sm text-gray-600">Certificate #{certificate.id}</p>
      </div>

      <div className="mb-8 border-b pb-4">
        <h2 className="text-xl font-bold mb-4">Project Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p>
              <span className="font-semibold">Contractor:</span> {project.name_of_contractor}
            </p>
            <p>
              <span className="font-semibold">Contract No:</span> {project.contract_no}
            </p>
            <p>
              <span className="font-semibold">Vote No:</span> {project.vote_no}
            </p>
          </div>
          <div>
            <p>
              <span className="font-semibold">Tender Sum:</span> {formatCurrency(project.tender_sum)}
            </p>
            <p>
              <span className="font-semibold">Date:</span> {formattedDate}
            </p>
            <p>
              <span className="font-semibold">Currency:</span> {certificate.currency}
            </p>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Certificate Summary</h2>
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2 text-left">Description</th>
              <th className="border p-2 text-right">Amount ({certificate.currency})</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="border p-2">Current Claim (Excl. VAT)</td>
              <td className="border p-2 text-right">{formatCurrency(certificate.current_claim_excl_vat)}</td>
            </tr>
            <tr>
              <td className="border p-2">VAT (15%)</td>
              <td className="border p-2 text-right">{formatCurrency(certificate.vat_value)}</td>
            </tr>
            <tr>
              <td className="border p-2">Previous Payment (Excl. VAT)</td>
              <td className="border p-2 text-right">{formatCurrency(certificate.previous_payment_excl_vat)}</td>
            </tr>
            <tr>
              <td className="border p-2">Value of Work Done (Incl. VAT)</td>
              <td className="border p-2 text-right">{formatCurrency(calculations.value_of_workdone_incl_vat)}</td>
            </tr>
            <tr>
              <td className="border p-2">Total Value of Work Done (Excl. VAT)</td>
              <td className="border p-2 text-right">{formatCurrency(calculations.total_value_of_workdone_excl_vat)}</td>
            </tr>
            <tr>
              <td className="border p-2">Retention (10%)</td>
              <td className="border p-2 text-right">{formatCurrency(calculations.retention)}</td>
            </tr>
            <tr className="font-bold bg-gray-50">
              <td className="border p-2">Total Amount Payable</td>
              <td className="border p-2 text-right">{formatCurrency(calculations.total_amount_payable)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Approval</h2>
        <div className="grid grid-cols-2 gap-8 mt-8">
          <div>
            <div className="border-t border-black pt-2 mt-16">
              <p className="font-semibold">Authorized Signature</p>
              <p className="text-sm text-gray-600">Project Manager</p>
            </div>
          </div>
          <div>
            <div className="border-t border-black pt-2 mt-16">
              <p className="font-semibold">Authorized Signature</p>
              <p className="text-sm text-gray-600">Finance Officer</p>
            </div>
          </div>
        </div>
      </div>

      <div className="text-xs text-gray-500 text-center mt-8 pt-4 border-t">
        <p>
          This certificate is issued without prejudice to the rights and obligations of the parties under the Contract.
        </p>
      </div>
    </div>
  )
}
