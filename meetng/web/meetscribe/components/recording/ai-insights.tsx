"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"

interface AIInsightsProps {
  isRecording: boolean
}

export function AIInsights({ isRecording }: AIInsightsProps) {
  const [insights, setInsights] = useState<string[]>([])

  useEffect(() => {
    if (!isRecording) return

    // Simulate AI insights being generated during recording
    const demoInsights = [
      "Key topics: Revenue growth, Customer acquisition, User retention",
      "Sentiment: Positive discussion about Q1 results",
      "Action items detected: Improve user retention rate to 90%",
      "Question raised: How can we reduce customer acquisition costs further?",
      "Suggestion: Consider implementing a referral program to improve retention",
    ]

    let currentIndex = 0

    const interval = setInterval(() => {
      if (currentIndex < demoInsights.length) {
        setInsights((prev) => [...prev, demoInsights[currentIndex]])
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [isRecording])

  return (
    <div className="space-y-4">
      {insights.length > 0 ? (
        insights.map((insight, index) => (
          <Card key={index}>
            <CardContent className="p-3 text-sm">{insight}</CardContent>
          </Card>
        ))
      ) : (
        <p className="text-muted-foreground text-sm">
          {isRecording ? "Analyzing conversation for insights..." : "Start recording to generate AI insights"}
        </p>
      )}
    </div>
  )
}

