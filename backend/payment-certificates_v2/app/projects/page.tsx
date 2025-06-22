"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { mockProjects } from "@/lib/mock-data"
import { formatCurrency } from "@/lib/utils"

export default function ProjectsPage() {
  const [projects, setProjects] = useState(mockProjects)

  const handleDelete = (id: string) => {
    setProjects(projects.filter((project) => project.id !== id))
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Projects</h1>
        <Button asChild>
          <Link href="/projects/new">Create New Project</Link>
        </Button>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-12">
          <h2 className="text-xl font-medium text-muted-foreground">No projects found</h2>
          <p className="mt-2">Create your first project to get started</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Card key={project.id} className="overflow-hidden">
              <CardHeader className="bg-muted/50">
                <CardTitle className="truncate">{project.name_of_contractor}</CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Contract No:</span>
                    <span className="font-medium">{project.contract_no}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Vote No:</span>
                    <span className="font-medium">{project.vote_no}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Tender Sum:</span>
                    <span className="font-medium">{formatCurrency(project.tender_sum)}</span>
                  </div>
                </div>

                <div className="flex justify-between mt-6 pt-4 border-t">
                  <Button variant="outline" asChild>
                    <Link href={`/projects/${project.id}`}>View Details</Link>
                  </Button>
                  <Button variant="outline" asChild>
                    <Link href={`/projects/${project.id}/certificates`}>Certificates</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
