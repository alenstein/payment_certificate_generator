import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b">
        <div className="container mx-auto py-4">
          <h1 className="text-2xl font-bold">Payment Certificates Generator</h1>
        </div>
      </header>

      <main className="flex-1 container mx-auto py-8">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h2 className="text-3xl font-bold tracking-tight">Generate Professional Payment Certificates</h2>
          <p className="text-xl text-muted-foreground">
            Create, manage, and export payment certificates for your projects with ease.
          </p>

          <div className="flex justify-center gap-4 pt-4">
            <Button asChild size="lg">
              <Link href="/projects">View Projects</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/projects/new">Create New Project</Link>
            </Button>
          </div>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-3">
          <div className="bg-card rounded-lg p-6 shadow-sm border">
            <h3 className="text-xl font-semibold mb-2">Project Management</h3>
            <p className="text-muted-foreground">
              Create and manage projects with contractor details, contract numbers, and tender sums.
            </p>
          </div>

          <div className="bg-card rounded-lg p-6 shadow-sm border">
            <h3 className="text-xl font-semibold mb-2">Certificate Generation</h3>
            <p className="text-muted-foreground">
              Generate certificates with automatic calculations for VAT, retention, and total payable amounts.
            </p>
          </div>

          <div className="bg-card rounded-lg p-6 shadow-sm border">
            <h3 className="text-xl font-semibold mb-2">PDF Export & Editing</h3>
            <p className="text-muted-foreground">
              Export certificates as professional PDFs and edit them before final download.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t py-6">
        <div className="container mx-auto text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} Payment Certificates Generator
        </div>
      </footer>
    </div>
  )
}
