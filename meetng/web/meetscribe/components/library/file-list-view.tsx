"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { FileText, BarChart, Play, Calendar, Clock } from "lucide-react"

interface Recording {
  id: string
  title: string
  date: Date
  duration: string
  hasTranscript: boolean
  hasFullTranscript: boolean
  hasAnalysis: boolean
}

interface FileListViewProps {
  recordings: Recording[]
  searchQuery: string
}

export function FileListView({ recordings, searchQuery }: FileListViewProps) {
  const [selectedRecordings, setSelectedRecordings] = useState<string[]>([])

  const filteredRecordings = recordings.filter((recording) => {
    if (!searchQuery) return true

    // Handle exact match with *
    if (searchQuery.includes("*")) {
      const exactTerms = searchQuery.split("*").filter(Boolean)
      return exactTerms.every((term) => recording.title.includes(term))
    }

    // Handle exclusion with -
    if (searchQuery.includes("-")) {
      const terms = searchQuery.split(" ")
      const includedTerms = terms.filter((term) => !term.startsWith("-"))
      const excludedTerms = terms.filter((term) => term.startsWith("-")).map((term) => term.substring(1))

      const includeMatch =
        includedTerms.length === 0 ||
        includedTerms.some((term) => recording.title.toLowerCase().includes(term.toLowerCase()))
      const excludeMatch = excludedTerms.some((term) => recording.title.toLowerCase().includes(term.toLowerCase()))

      return includeMatch && !excludeMatch
    }

    // Regular search
    return recording.title.toLowerCase().includes(searchQuery.toLowerCase())
  })

  const handleSelectRecording = (id: string) => {
    setSelectedRecordings((prev) => (prev.includes(id) ? prev.filter((recId) => recId !== id) : [...prev, id]))
  }

  const handleSelectAll = () => {
    if (selectedRecordings.length === filteredRecordings.length) {
      setSelectedRecordings([])
    } else {
      setSelectedRecordings(filteredRecordings.map((rec) => rec.id))
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Checkbox
            id="select-all"
            checked={selectedRecordings.length === filteredRecordings.length && filteredRecordings.length > 0}
            onCheckedChange={handleSelectAll}
          />
          <label htmlFor="select-all" className="text-sm">
            Select All ({filteredRecordings.length})
          </label>
        </div>

        {selectedRecordings.length > 0 && (
          <div className="flex gap-2">
            <Button size="sm" variant="outline">
              <FileText className="h-3.5 w-3.5 mr-1" /> Transcribe
            </Button>
            <Button size="sm" variant="outline">
              <BarChart className="h-3.5 w-3.5 mr-1" /> Analyze
            </Button>
          </div>
        )}
      </div>

      {filteredRecordings.length > 0 ? (
        <div className="space-y-2">
          {filteredRecordings.map((recording) => (
            <Card key={recording.id} className="overflow-hidden">
              <CardContent className="p-0">
                <div className="flex items-center p-4">
                  <Checkbox
                    id={`recording-${recording.id}`}
                    checked={selectedRecordings.includes(recording.id)}
                    onCheckedChange={() => handleSelectRecording(recording.id)}
                    className="mr-4"
                  />

                  <div className="flex-1">
                    <h3 className="font-medium">{recording.title}</h3>
                    <div className="flex items-center text-sm text-muted-foreground mt-1">
                      <Calendar className="h-3.5 w-3.5 mr-1" />
                      <span>{recording.date.toLocaleDateString()}</span>
                      <span className="mx-2">•</span>
                      <Clock className="h-3.5 w-3.5 mr-1" />
                      <span>{recording.duration}</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost">
                      <Play className="h-4 w-4" />
                    </Button>

                    {recording.hasTranscript && (
                      <Button size="sm" variant="outline">
                        <FileText className="h-4 w-4 mr-1" />
                        {recording.hasFullTranscript ? "Transcript" : "Partial"}
                      </Button>
                    )}

                    {recording.hasAnalysis && (
                      <Button size="sm" variant="outline">
                        <BarChart className="h-4 w-4 mr-1" />
                        Analysis
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="flex items-center justify-center h-40 border rounded-md">
          <p className="text-muted-foreground">No recordings match your search criteria</p>
        </div>
      )}
    </div>
  )
}

