"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { createProject, mockProjects } from "@/lib/mock-data"

export default function NewProjectPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name_of_contractor: "",
    contract_no: "",
    vote_no: "",
    tender_sum: "",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Create new project
    const newProject = createProject({
      name_of_contractor: formData.name_of_contractor,
      contract_no: formData.contract_no,
      vote_no: formData.vote_no,
      tender_sum: Number.parseFloat(formData.tender_sum) || 0,
    })

    // In a real app, we would save to the database
    // For now, we'll just add to our mock data
    mockProjects.push(newProject)

    // Redirect to projects list
    router.push("/projects")
  }

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Create New Project</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name_of_contractor">Contractor Name</Label>
                <Input
                  id="name_of_contractor"
                  name="name_of_contractor"
                  value={formData.name_of_contractor}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="contract_no">Contract Number</Label>
                <Input
                  id="contract_no"
                  name="contract_no"
                  value={formData.contract_no}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="vote_no">Vote Number</Label>
                <Input id="vote_no" name="vote_no" value={formData.vote_no} onChange={handleChange} required />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tender_sum">Tender Sum</Label>
                <Input
                  id="tender_sum"
                  name="tender_sum"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.tender_sum}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => router.push("/projects")}>
                  Cancel
                </Button>
                <Button type="submit">Create Project</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
