"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { mockProjects, mockCertificates, mockCalculations } from "@/lib/mock-data"
import { formatCurrency } from "@/lib/utils"
import type { Project, Certificate, Calculations } from "@/lib/types"
import CertificatePDF from "@/components/certificate-pdf"

export default function CertificateDetailPage({
  params,
}: {
  params: { id: string; certId: string }
}) {
  const router = useRouter()
  const [project, setProject] = useState<Project | null>(null)
  const [certificate, setCertificate] = useState<Certificate | null>(null)
  const [calculations, setCalculations] = useState<Calculations | null>(null)
  const [activeTab, setActiveTab] = useState("details")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    try {
      // Find project by ID
      const foundProject = mockProjects.find((p) => p.id === params.id)
      if (!foundProject) {
        setError("Project not found")
        return
      }

      // Find certificate by ID
      const foundCertificate = mockCertificates.find((c) => c.id === params.certId)
      if (!foundCertificate) {
        setError("Certificate not found")
        return
      }

      // Find calculations for this certificate
      const foundCalculations = mockCalculations.find((c) => c.certificate_id === params.certId)
      if (!foundCalculations) {
        setError("Calculations not found")
        return
      }

      setProject(foundProject)
      setCertificate(foundCertificate)
      setCalculations(foundCalculations)
      setIsLoading(false)
    } catch (err) {
      setError("An error occurred while loading data")
      console.error(err)
    }
  }, [params.id, params.certId])

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h2 className="text-xl font-bold text-red-500 mb-4">{error}</h2>
          <Button asChild>
            <Link href="/projects">Back to Projects</Link>
          </Button>
        </div>
      </div>
    )
  }

  if (!project || !certificate || !calculations) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h2 className="text-xl font-bold text-red-500 mb-4">Data not available</h2>
          <Button asChild>
            <Link href="/projects">Back to Projects</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Certificate Details</h1>
        <div className="space-x-2">
          <Button variant="outline" asChild>
            <Link href={`/projects/${project.id}`}>Back to Project</Link>
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="details">Certificate Details</TabsTrigger>
          <TabsTrigger value="preview">PDF Preview</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Certificate Information</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="space-y-4">
                  <div className="flex justify-between">
                    <dt className="font-medium">Project:</dt>
                    <dd>{project.name_of_contractor}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="font-medium">Contract No:</dt>
                    <dd>{project.contract_no}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="font-medium">Currency:</dt>
                    <dd>{certificate.currency}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="font-medium">Current Claim (Excl. VAT):</dt>
                    <dd>{formatCurrency(certificate.current_claim_excl_vat)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="font-medium">VAT Value:</dt>
                    <dd>{formatCurrency(certificate.vat_value)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="font-medium">Previous Payment (Excl. VAT):</dt>
                    <dd>{formatCurrency(certificate.previous_payment_excl_vat)}</dd>
                  </div>
                </dl>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Calculations</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="space-y-4">
                  <div className="flex justify-between">
                    <dt className="font-medium">Value of Work Done (Incl. VAT):</dt>
                    <dd>{formatCurrency(calculations.value_of_workdone_incl_vat)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="font-medium">Total Value of Work Done (Excl. VAT):</dt>
                    <dd>{formatCurrency(calculations.total_value_of_workdone_excl_vat)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="font-medium">Retention (10%):</dt>
                    <dd>{formatCurrency(calculations.retention)}</dd>
                  </div>
                  <div className="flex justify-between border-t pt-4 mt-4">
                    <dt className="font-medium text-lg">Total Amount Payable:</dt>
                    <dd className="font-bold text-lg">{formatCurrency(calculations.total_amount_payable)}</dd>
                  </div>
                </dl>
              </CardContent>
            </Card>
          </div>

          <div className="mt-6 flex justify-end">
            <Button onClick={() => setActiveTab("preview")}>Preview Certificate PDF</Button>
          </div>
        </TabsContent>

        <TabsContent value="preview">
          <Card className="overflow-hidden">
            <CardHeader className="bg-muted/50">
              <CardTitle>Certificate PDF Preview</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {project && certificate && calculations && (
                <div className="bg-white border rounded-lg shadow-sm p-8 max-w-4xl mx-auto">
                  <CertificatePDF project={project} certificate={certificate} calculations={calculations} />
                </div>
              )}

              <div className="flex justify-end mt-6 space-x-2">
                <Button variant="outline">Edit PDF</Button>
                <Button>Download PDF</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
