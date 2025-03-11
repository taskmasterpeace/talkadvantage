"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { RefreshCw, X, HelpCircle, Send, SkipForward } from "lucide-react"

interface CuriosityEngineProps {
  hasContent: boolean
}

export default function CuriosityEngine({ hasContent }: CuriosityEngineProps) {
  const [questions, setQuestions] = useState<Array<{ id: number; text: string; answered?: boolean; answer?: string }>>(
    [],
  )
  const [currentAnswer, setCurrentAnswer] = useState("")

  const generateQuestions = () => {
    // Demo questions
    setQuestions([
      { id: 1, text: "What are the main risks to the project timeline?" },
      { id: 2, text: "How will the additional features impact the development resources?" },
      { id: 3, text: "What specific user experience concerns were mentioned?" },
      { id: 4, text: "Who will be responsible for the follow-up meeting?" },
    ])
  }

  const clearQuestions = () => {
    setQuestions([])
  }

  const submitAnswer = (id: number) => {
    if (!currentAnswer.trim()) return

    setQuestions(questions.map((q) => (q.id === id ? { ...q, answered: true, answer: currentAnswer } : q)))
    setCurrentAnswer("")
  }

  const skipQuestion = (id: number) => {
    setQuestions(questions.filter((q) => q.id !== id))
  }

  if (!hasContent) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <HelpCircle className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">Curiosity Engine</h3>
        <p className="text-muted-foreground mb-4">
          Start recording to generate AI-powered questions about your conversation.
        </p>
        <Button variant="outline" disabled>
          Generate Questions
        </Button>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <HelpCircle className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">No Questions Yet</h3>
        <p className="text-muted-foreground mb-4">Generate questions to explore insights from your conversation.</p>
        <Button onClick={generateQuestions}>Generate Questions</Button>
      </div>
    )
  }

  const unansweredQuestions = questions.filter((q) => !q.answered)
  const answeredQuestions = questions.filter((q) => q.answered)

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-2">
        <h3 className="font-medium">Questions</h3>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={generateQuestions}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={clearQuestions}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 p-2 overflow-y-auto space-y-4">
        {/* Unanswered Questions */}
        {unansweredQuestions.length > 0 && (
          <div className="space-y-4">
            {unansweredQuestions.map((question) => (
              <Card key={question.id} className="p-4">
                <p className="font-medium mb-2">{question.text}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Input
                    placeholder="Your answer..."
                    value={currentAnswer}
                    onChange={(e) => setCurrentAnswer(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        submitAnswer(question.id)
                      }
                    }}
                  />
                  <Button size="icon" onClick={() => submitAnswer(question.id)}>
                    <Send className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => skipQuestion(question.id)}>
                    <SkipForward className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Answered Questions */}
        {answeredQuestions.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground">Answered Questions</h4>
            {answeredQuestions.map((question) => (
              <Card key={question.id} className="p-3 bg-muted/30">
                <p className="font-medium text-sm">{question.text}</p>
                <p className="text-sm mt-1">{question.answer}</p>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

