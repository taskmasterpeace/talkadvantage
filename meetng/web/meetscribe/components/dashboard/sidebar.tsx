"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Mic, Library, FileText, BarChart, Upload, Settings, HelpCircle, LogOut, BrainCircuit } from "lucide-react"

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="hidden md:flex w-64 flex-col border-r bg-muted/40 h-screen">
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-xl">
          <BrainCircuit className="h-6 w-6 text-primary" />
          <span>MeetScribe</span>
        </Link>
      </div>
      <div className="flex-1 overflow-auto py-2">
        <nav className="grid gap-1 px-2">
          <Link href="/dashboard/record">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-2", pathname === "/dashboard/record" && "bg-muted")}
            >
              <Mic className="h-4 w-4" />
              Record
            </Button>
          </Link>
          <Link href="/dashboard/library">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-2", pathname === "/dashboard/library" && "bg-muted")}
            >
              <Library className="h-4 w-4" />
              Library
            </Button>
          </Link>
          <Link href="/dashboard/transcripts">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-2", pathname === "/dashboard/transcripts" && "bg-muted")}
            >
              <FileText className="h-4 w-4" />
              Transcripts
            </Button>
          </Link>
          <Link href="/dashboard/analysis">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-2", pathname === "/dashboard/analysis" && "bg-muted")}
            >
              <BarChart className="h-4 w-4" />
              Analysis
            </Button>
          </Link>
          <Link href="/dashboard/import">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-2", pathname === "/dashboard/import" && "bg-muted")}
            >
              <Upload className="h-4 w-4" />
              Import
            </Button>
          </Link>
        </nav>
      </div>
      <div className="border-t p-2">
        <nav className="grid gap-1">
          <Link href="/dashboard/settings">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-2", pathname === "/dashboard/settings" && "bg-muted")}
            >
              <Settings className="h-4 w-4" />
              Settings
            </Button>
          </Link>
          <Link href="/dashboard/help">
            <Button
              variant="ghost"
              className={cn("w-full justify-start gap-2", pathname === "/dashboard/help" && "bg-muted")}
            >
              <HelpCircle className="h-4 w-4" />
              Help & Support
            </Button>
          </Link>
          <Link href="/logout">
            <Button variant="ghost" className="w-full justify-start gap-2 text-muted-foreground">
              <LogOut className="h-4 w-4" />
              Log out
            </Button>
          </Link>
        </nav>
      </div>
    </div>
  )
}

