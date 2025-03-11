"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Check, X } from "lucide-react"

interface AIInsightsProps {
  isRecording: boolean
}

interface Question {
  id: string
  text: string
  answered: boolean
  answer?: string
}

export function CuriosityEngine({ isRecording }: AIInsightsProps) {
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentAnswer, setCurrentAnswer] = useState("")
  const [answeringId, setAnsweringId] = useState<string | null>(null)

  useEffect(() => {
    if (!isRecording) return

    // Simulate questions being generated during recording
    const demoQuestions = [
      "What specific strategies led to the 15% revenue growth?",
      "Which marketing channels had the lowest customer acquisition cost?",
      "What factors are currently affecting the user retention rate?",
      "Are there any seasonal patterns in the Q1 results?",
      "How does the team plan to achieve the 90% retention target?",
    ]

    let currentIndex = 0

    const interval = setInterval(() => {
      if (currentIndex < demoQuestions.length) {
        setQuestions((prev) => [
          ...prev,
          {
            id: `q-${Date.now()}-${currentIndex}`,
            text: demoQuestions[currentIndex],
            answered: false,
          },
        ])
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 6000)

    return () => clearInterval(interval)
  }, [isRecording])

  const handleAnswer = (id: string) => {
    setQuestions((prev) => prev.map((q) => (q.id === id ? { ...q, answered: true, answer: currentAnswer } : q)))
    setCurrentAnswer("")
    setAnsweringId(null)
  }

  const handleSkip = (id: string) => {
    setQuestions((prev) => prev.filter((q) => q.id !== id))
  }

  return (
    <div className="space-y-4">
      {questions.length > 0 ? (
        questions.map((question) => (
          <Card key={question.id}>
            <CardContent className="p-3 pt-4 text-sm">
              <p className="font-medium">{question.text}</p>
              {question.answered && <p className="mt-2 text-muted-foreground">Answer: {question.answer}</p>}
            </CardContent>
            {!question.answered && (
              <CardFooter className="p-3 pt-0 flex gap-2">
                {answeringId === question.id ? (
                  <>
                    <Input
                      value={currentAnswer}
                      onChange={(e) => setCurrentAnswer(e.target.value)}
                      placeholder="Type your answer..."
                      className="text-sm"
                    />
                    <Button size="sm" variant="ghost" onClick={() => handleAnswer(question.id)}>
                      <Check className="h-4 w-4" />
                    </Button>
                  </>
                ) : (
                  <>
                    <Button size="sm" variant="outline" onClick={() => setAnsweringId(question.id)} className="flex-1">
                      Answer
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleSkip(question.id)}>
                      <X className="h-4 w-4" />
                    </Button>
                  </>
                )}
              </CardFooter>
            )}
          </Card>
        ))
      ) : (
        <p className="text-muted-foreground text-sm">
          {isRecording ? "Generating questions based on the conversation..." : "Start recording to generate questions"}
        </p>
      )}
    </div>
  )
}

