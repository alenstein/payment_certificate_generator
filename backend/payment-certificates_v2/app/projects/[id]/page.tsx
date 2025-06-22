"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { mockProjects, mockCertificates } from "@/lib/mock-data"
import { formatCurrency } from "@/lib/utils"
import type { Project } from "@/lib/types"

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [project, setProject] = useState<Project | null>(null)
  const [certificates, setCertificates] = useState<any[]>([])
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

      setProject(foundProject)

      // Find certificates for this project
      const projectCertificates = mockCertificates.filter((c) => c.project_id === params.id)
      setCertificates(projectCertificates)
      setIsLoading(false)
    } catch (err) {
      setError("An error occurred while loading data")
      console.error(err)
    }
  }, [params.id])

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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Project Details</h1>
        <div className="space-x-2">
          <Button variant="outline" asChild>
            <Link href="/projects">Back to Projects</Link>
          </Button>
          <Button asChild>
            <Link href={`/projects/${project.id}/certificates/new`}>Create Certificate</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-4">
              <div className="flex justify-between">
                <dt className="font-medium">Contractor:</dt>
                <dd>{project.name_of_contractor}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-medium">Contract No:</dt>
                <dd>{project.contract_no}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-medium">Vote No:</dt>
                <dd>{project.vote_no}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-medium">Tender Sum:</dt>
                <dd>{formatCurrency(project.tender_sum)}</dd>
              </div>
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Certificates</CardTitle>
          </CardHeader>
          <CardContent>
            {certificates.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground">No certificates yet</p>
                <Button className="mt-2" asChild>
                  <Link href={`/projects/${project.id}/certificates/new`}>Create Certificate</Link>
                </Button>
              </div>
            ) : (
              <ul className="space-y-2">
                {certificates.map((cert) => (
                  <li key={cert.id} className="flex justify-between items-center p-2 border rounded hover:bg-muted/50">
                    <span>Certificate #{cert.id}</span>
                    <Button variant="outline" size="sm" asChild>
                      <Link href={`/projects/${project.id}/certificates/${cert.id}`}>View</Link>
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
