"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  FolderOpen,
  RefreshCw,
  Search,
  FileText,
  BarChart,
  Play,
  Pause,
} from "lucide-react"

export default function LibraryPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [includeSubfolders, setIncludeSubfolders] = useState(false)
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)
  const [viewMode, setViewMode] = useState<"calendar" | "files">("calendar")
  const [selectedRecordings, setSelectedRecordings] = useState<string[]>([])

  const previousMonth = () => {
    const prevMonth = new Date(currentMonth)
    prevMonth.setMonth(prevMonth.getMonth() - 1)
    setCurrentMonth(prevMonth)
  }

  const nextMonth = () => {
    const nextMonth = new Date(currentMonth)
    nextMonth.setMonth(nextMonth.getMonth() + 1)
    setCurrentMonth(nextMonth)
  }

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date)
  }

  const handleSelectRecording = (id: string) => {
    setSelectedRecordings((prev) => (prev.includes(id) ? prev.filter((recId) => recId !== id) : [...prev, id]))
  }

  const getRecordingsForDate = (date: Date | null) => {
    if (!date) return []
    return mockRecordings.filter(
      (recording) =>
        recording.date.getDate() === date.getDate() &&
        recording.date.getMonth() === date.getMonth() &&
        recording.date.getFullYear() === date.getFullYear(),
    )
  }

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
        <div className="flex gap-2">
          <Button variant="outline">
            <FolderOpen className="h-4 w-4 mr-2" /> Select Folder
          </Button>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" /> Refresh
          </Button>
          <div className="flex items-center gap-2">
            <Checkbox
              id="include-subfolders"
              checked={includeSubfolders}
              onCheckedChange={(checked) => setIncludeSubfolders(checked as boolean)}
            />
            <label htmlFor="include-subfolders" className="text-sm cursor-pointer">
              Include Subfolders
            </label>
          </div>
        </div>
        <div className="flex gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Filter files... (Use * for exact match, - to exclude)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button variant="outline" onClick={() => setViewMode(viewMode === "calendar" ? "files" : "calendar")}>
            {viewMode === "calendar" ? (
              <>
                <FileText className="h-4 w-4 mr-2" /> List View
              </>
            ) : (
              <>
                <Calendar className="h-4 w-4 mr-2" /> Calendar View
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          {viewMode === "calendar" ? (
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <Button variant="outline" size="sm" onClick={previousMonth}>
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <h2 className="text-lg font-medium">
                    {currentMonth.toLocaleString("default", { month: "long", year: "numeric" })}
                  </h2>
                  <Button variant="outline" size="sm" onClick={nextMonth}>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>

                {/* Calendar Header */}
                <div className="grid grid-cols-7 gap-1 mb-1">
                  {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                    <div key={day} className="text-center font-medium py-2">
                      {day}
                    </div>
                  ))}
                </div>

                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-1">
                  {generateCalendarDays(currentMonth).map((date, i) => {
                    const isCurrentMonth = date.getMonth() === currentMonth.getMonth()
                    const isSelected =
                      selectedDate &&
                      date.getDate() === selectedDate.getDate() &&
                      date.getMonth() === selectedDate.getMonth() &&
                      date.getFullYear() === selectedDate.getFullYear()

                    const hasRecordings = mockRecordings.some(
                      (r) =>
                        r.date.getDate() === date.getDate() &&
                        r.date.getMonth() === date.getMonth() &&
                        r.date.getFullYear() === date.getFullYear(),
                    )

                    const hasTranscripts = mockRecordings.some(
                      (r) =>
                        r.date.getDate() === date.getDate() &&
                        r.date.getMonth() === date.getMonth() &&
                        r.date.getFullYear() === date.getFullYear() &&
                        r.hasTranscript,
                    )

                    const hasPartialTranscripts = mockRecordings.some(
                      (r) =>
                        r.date.getDate() === date.getDate() &&
                        r.date.getMonth() === date.getMonth() &&
                        r.date.getFullYear() === date.getFullYear() &&
                        r.hasTranscript &&
                        !r.hasFullTranscript,
                    )

                    let statusClass = ""
                    if (hasTranscripts && !hasPartialTranscripts) statusClass = "has-transcript"
                    else if (hasPartialTranscripts) statusClass = "has-partial"
                    else if (hasRecordings) statusClass = "has-recording"

                    return (
                      <div
                        key={i}
                        className={`calendar-day ${!isCurrentMonth ? "text-muted-foreground opacity-50" : ""} 
                                   ${isSelected ? "selected" : ""} ${statusClass}`}
                        onClick={() => handleDateSelect(date)}
                      >
                        <div className="text-center">{date.getDate()}</div>
                      </div>
                    )
                  })}
                </div>

                <div className="flex flex-wrap gap-4 mt-4 text-sm">
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full bg-background border border-primary mr-2"></div>
                    <span>No Recordings</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full bg-success/20 mr-2"></div>
                    <span>Has Recordings</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full bg-warning/20 mr-2"></div>
                    <span>Partial Transcript</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full bg-info/20 mr-2"></div>
                    <span>Full Transcript</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-4">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-2">
                    <Checkbox
                      id="select-all"
                      checked={selectedRecordings.length === mockRecordings.length && mockRecordings.length > 0}
                      onCheckedChange={() => {
                        if (selectedRecordings.length === mockRecordings.length) {
                          setSelectedRecordings([])
                        } else {
                          setSelectedRecordings(mockRecordings.map((r) => r.id))
                        }
                      }}
                    />
                    <label htmlFor="select-all" className="text-sm cursor-pointer">
                      Select All ({mockRecordings.length})
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

                <div className="space-y-2">
                  {mockRecordings.map((recording) => (
                    <div key={recording.id} className="flex items-center p-3 border rounded-md">
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
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div>
          <Card className="h-full">
            <CardContent className="p-4 h-full flex flex-col">
              <div className="mb-4">
                <h3 className="text-lg font-medium mb-2">Recording Details</h3>
                {selectedDate ? (
                  <p>Recordings for {selectedDate.toLocaleDateString()}</p>
                ) : (
                  <p className="text-muted-foreground">Select a date to view recordings</p>
                )}
              </div>

              {selectedDate && getRecordingsForDate(selectedDate).length > 0 ? (
                <div className="flex-1 space-y-4">
                  <Tabs defaultValue="recordings">
                    <TabsList className="w-full">
                      <TabsTrigger value="recordings" className="flex-1">
                        Recordings
                      </TabsTrigger>
                      <TabsTrigger value="player" className="flex-1">
                        Player
                      </TabsTrigger>
                    </TabsList>
                    <TabsContent value="recordings" className="space-y-4 mt-4">
                      {getRecordingsForDate(selectedDate).map((recording) => (
                        <div key={recording.id} className="border rounded-md p-3">
                          <h4 className="font-medium">{recording.title}</h4>
                          <p className="text-sm text-muted-foreground">{recording.duration}</p>
                          <div className="flex gap-2 mt-2">
                            <Button size="sm" variant="outline" className="text-xs">
                              <FileText className="h-3 w-3 mr-1" /> Transcript
                            </Button>
                            <Button size="sm" variant="outline" className="text-xs">
                              <BarChart className="h-3 w-3 mr-1" /> Analysis
                            </Button>
                          </div>
                        </div>
                      ))}
                    </TabsContent>
                    <TabsContent value="player" className="mt-4 flex-1">
                      <div className="space-y-4 h-full flex flex-col">
                        <div className="waveform-container flex-1">
                          <div className="waveform">
                            {Array.from({ length: 50 }).map((_, i) => (
                              <div
                                key={i}
                                className="waveform-bar"
                                style={{
                                  height: `${Math.sin(i * 0.2) * 20 + 30}%`,
                                }}
                              />
                            ))}
                          </div>
                        </div>
                        <div className="text-center text-sm">
                          <span>0:00</span> / <span>45:12</span>
                        </div>
                        <div className="flex justify-center gap-2">
                          <Button size="sm" variant="outline">
                            <Play className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Pause className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>

                  <div className="mt-auto pt-4 flex justify-between">
                    <Button variant="outline" size="sm">
                      Transcribe Selected
                    </Button>
                    <Button size="sm">Send to Analysis</Button>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <p className="text-muted-foreground text-center">
                    {selectedDate ? "No recordings found for this date" : "Select a date to view recordings"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="mt-4 flex justify-end gap-2">
        <Button variant="outline">Transcribe Selected</Button>
        <Button variant="outline">View Transcript</Button>
        <Button variant="outline">Send to Live Analysis</Button>
        <Button>Send to Deep Analysis</Button>
      </div>
    </div>
  )
}

interface Recording {
  id: string
  title: string
  date: Date
  duration: string
  hasTranscript: boolean
  hasFullTranscript: boolean
  hasAnalysis: boolean
}

const mockRecordings: Recording[] = [
  {
    id: "1",
    title: "Weekly Team Meeting",
    date: new Date(2025, 2, 6), // March 6, 2025
    duration: "45:12",
    hasTranscript: true,
    hasFullTranscript: true,
    hasAnalysis: true,
  },
  {
    id: "2",
    title: "Client Interview - Project Alpha",
    date: new Date(2025, 2, 6), // March 6, 2025
    duration: "32:47",
    hasTranscript: true,
    hasFullTranscript: false,
    hasAnalysis: false,
  },
  {
    id: "3",
    title: "Product Planning Session",
    date: new Date(2025, 2, 4), // March 4, 2025
    duration: "1:12:33",
    hasTranscript: true,
    hasFullTranscript: true,
    hasAnalysis: true,
  },
  {
    id: "4",
    title: "Marketing Strategy Discussion",
    date: new Date(2025, 2, 2), // March 2, 2025
    duration: "28:05",
    hasTranscript: true,
    hasFullTranscript: false,
    hasAnalysis: false,
  },
  {
    id: "5",
    title: "Quarterly Planning - Q1 2025",
    date: new Date(2025, 1, 28), // February 28, 2025
    duration: "1:45:22",
    hasTranscript: true,
    hasFullTranscript: true,
    hasAnalysis: true,
  },
  {
    id: "6",
    title: "User Research Interviews",
    date: new Date(2025, 1, 24), // February 24, 2025
    duration: "52:18",
    hasTranscript: true,
    hasFullTranscript: true,
    hasAnalysis: true,
  },
]

function generateCalendarDays(month: Date): Date[] {
  const year = month.getFullYear()
  const monthIndex = month.getMonth()

  // First day of the month
  const firstDay = new Date(year, monthIndex, 1)
  // Last day of the month
  const lastDay = new Date(year, monthIndex + 1, 0)

  // Get the day of the week for the first day (0 = Sunday, 6 = Saturday)
  const firstDayOfWeek = firstDay.getDay()

  // Calculate days from previous month to show
  const daysFromPrevMonth = firstDayOfWeek

  // Calculate total days to show (previous month days + current month days + next month days)
  // We want to show 6 weeks (42 days) to keep the calendar consistent
  const totalDays = 42

  const days: Date[] = []

  // Add days from previous month
  const prevMonth = new Date(year, monthIndex, 0)
  const prevMonthLastDay = prevMonth.getDate()

  for (let i = prevMonthLastDay - daysFromPrevMonth + 1; i <= prevMonthLastDay; i++) {
    days.push(new Date(year, monthIndex - 1, i))
  }

  // Add days from current month
  const currentMonthDays = lastDay.getDate()
  for (let i = 1; i <= currentMonthDays; i++) {
    days.push(new Date(year, monthIndex, i))
  }

  // Add days from next month
  const remainingDays = totalDays - days.length
  for (let i = 1; i <= remainingDays; i++) {
    days.push(new Date(year, monthIndex + 1, i))
  }

  return days
}

