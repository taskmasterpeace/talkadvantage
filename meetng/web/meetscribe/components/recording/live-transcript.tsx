"use client"

import { useEffect, useState } from "react"

interface LiveTranscriptProps {
  isRecording: boolean
}

export function LiveTranscript({ isRecording }: LiveTranscriptProps) {
  const [transcript, setTranscript] = useState("")

  useEffect(() => {
    if (!isRecording) return

    // This is a simulation of live transcription
    // In a real app, this would connect to a transcription service
    const demoTexts = [
      "Hello and welcome to our weekly team meeting.",
      "Today we'll be discussing the Q1 results and our plans for Q2.",
      "Let's start by reviewing our key metrics from the last quarter.",
      "Revenue grew by 15% compared to the previous quarter, which exceeded our target of 12%.",
      "Customer acquisition cost decreased by 8%, which is a positive trend.",
      "Our user retention rate remained stable at 85%, but we're aiming to improve this to 90% in Q2.",
    ]

    let currentIndex = 0

    const interval = setInterval(() => {
      if (currentIndex < demoTexts.length) {
        setTranscript((prev) => prev + (prev ? " " : "") + demoTexts[currentIndex])
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [isRecording])

  return (
    <div className="min-h-[200px] border rounded-md p-4 bg-background">
      {isRecording && transcript ? (
        <p>{transcript}</p>
      ) : isRecording ? (
        <div className="flex items-center text-muted-foreground">
          <span className="recording-dot"></span>
          Listening...
        </div>
      ) : (
        <p className="text-muted-foreground">Start recording to see live transcription</p>
      )}
    </div>
  )
}

