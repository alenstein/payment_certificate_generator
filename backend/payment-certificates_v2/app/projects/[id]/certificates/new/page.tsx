"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { mockProjects, mockCertificates, createCertificate, calculateValues, mockCalculations } from "@/lib/mock-data"
import type { Project } from "@/lib/types"

export default function NewCertificatePage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [project, setProject] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    currency: "USD",
    current_claim_excl_vat: "",
    previous_payment_excl_vat: "",
  })

  useEffect(() => {
    try {
      // Find project by ID
      const foundProject = mockProjects.find((p) => p.id === params.id)
      if (!foundProject) {
        setError("Project not found")
        return
      }

      setProject(foundProject)
      setIsLoading(false)
    } catch (err) {
      setError("An error occurred while loading data")
      console.error(err)
    }
  }, [params.id])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleCurrencyChange = (value: string) => {
    setFormData((prev) => ({ ...prev, currency: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!project) return

    try {
      // Calculate VAT (15% of current claim)
      const current_claim_excl_vat = Number.parseFloat(formData.current_claim_excl_vat) || 0
      const vat_value = current_claim_excl_vat * 0.15

      // Create new certificate
      const newCertificate = createCertificate({
        project_id: project.id,
        currency: formData.currency,
        current_claim_excl_vat,
        vat_value,
        previous_payment_excl_vat: Number.parseFloat(formData.previous_payment_excl_vat) || 0,
      })

      // Calculate values
      const calculations = calculateValues(newCertificate)

      // In a real app, we would save to the database
      // For now, we'll just add to our mock data
      mockCertificates.push(newCertificate)
      mockCalculations.push(calculations)

      // Redirect to certificate view
      router.push(`/projects/${project.id}/certificates/${newCertificate.id}`)
    } catch (err) {
      setError("An error occurred while creating the certificate")
      console.error(err)
    }
  }

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

  if (!project) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h2 className="text-xl font-bold text-red-500 mb-4">Project not found</h2>
          <Button asChild>
            <Link href="/projects">Back to Projects</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Create New Certificate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-6">
              <h2 className="text-lg font-medium">Project: {project.name_of_contractor}</h2>
              <p className="text-muted-foreground">Contract: {project.contract_no}</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <Select value={formData.currency} onValueChange={handleCurrencyChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select currency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="USD">USD</SelectItem>
                    <SelectItem value="ZIG">ZIG</SelectItem>
                    <SelectItem value="EUR">EUR</SelectItem>
                    <SelectItem value="GBP">GBP</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="current_claim_excl_vat">Current Claim (Excl. VAT)</Label>
                <Input
                  id="current_claim_excl_vat"
                  name="current_claim_excl_vat"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.current_claim_excl_vat}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="previous_payment_excl_vat">Previous Payment (Excl. VAT)</Label>
                <Input
                  id="previous_payment_excl_vat"
                  name="previous_payment_excl_vat"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.previous_payment_excl_vat}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => router.push(`/projects/${project.id}`)}>
                  Cancel
                </Button>
                <Button type="submit">Create Certificate</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
