"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"

interface Recording {
  id: string
  title: string
  date: Date
  duration: string
  hasTranscript: boolean
  hasFullTranscript: boolean
  hasAnalysis: boolean
}

interface CalendarViewProps {
  currentMonth: Date
  selectedDate: Date | null
  onSelectDate: (date: Date) => void
  recordings: Recording[]
}

export function CalendarView({ currentMonth, selectedDate, onSelectDate, recordings }: CalendarViewProps) {
  const [calendarDays, setCalendarDays] = useState<Date[]>([])

  useEffect(() => {
    const days = generateCalendarDays(currentMonth)
    setCalendarDays(days)
  }, [currentMonth])

  const handleDateClick = (date: Date) => {
    onSelectDate(date)
  }

  const getDateStatus = (date: Date) => {
    const recordingsForDate = recordings.filter(
      (recording) =>
        recording.date.getDate() === date.getDate() &&
        recording.date.getMonth() === date.getMonth() &&
        recording.date.getFullYear() === date.getFullYear(),
    )

    if (recordingsForDate.length === 0) return "none"

    const hasFullTranscript = recordingsForDate.some((r) => r.hasFullTranscript)
    const hasPartialTranscript = recordingsForDate.some((r) => r.hasTranscript && !r.hasFullTranscript)

    if (hasFullTranscript) return "transcript"
    if (hasPartialTranscript) return "partial"
    return "recording"
  }

  return (
    <div className="grid grid-cols-7 gap-1">
      {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
        <div key={day} className="text-center font-medium py-2">
          {day}
        </div>
      ))}

      {calendarDays.map((date, i) => {
        const isCurrentMonth = date.getMonth() === currentMonth.getMonth()
        const isSelected =
          selectedDate &&
          date.getDate() === selectedDate.getDate() &&
          date.getMonth() === selectedDate.getMonth() &&
          date.getFullYear() === selectedDate.getFullYear()

        const dateStatus = getDateStatus(date)

        return (
          <div
            key={i}
            className={cn(
              "calendar-day",
              !isCurrentMonth && "text-muted-foreground opacity-50",
              isSelected && "selected",
              dateStatus === "recording" && "has-recording",
              dateStatus === "partial" && "has-partial",
              dateStatus === "transcript" && "has-transcript",
              "cursor-pointer",
            )}
            onClick={() => handleDateClick(date)}
          >
            <div className="text-center">{date.getDate()}</div>
          </div>
        )
      })}
    </div>
  )
}

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

