"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Mic, MicOff, Pause, Play, Save, Bookmark, RefreshCw, Copy, FileText } from "lucide-react"

export default function RecordPage() {
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [sessionName, setSessionName] = useState("")
  const [selectedTemplate, setSelectedTemplate] = useState("full-analysis")
  const [processingMode, setProcessingMode] = useState("manual")
  const [liveText, setLiveText] = useState("")
  const [aiInsights, setAiInsights] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState("insights")
  const [questions, setQuestions] = useState<{ id: string; text: string; answered: boolean; answer?: string }[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      audioContextRef.current = new AudioContext()
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setIsPaused(false)

      timerRef.current = setInterval(() => {
        setRecordingTime((prevTime) => prevTime + 1)
      }, 1000)

      // Simulate live transcription
      simulateLiveTranscription()

      // Simulate AI insights
      simulateAIInsights()

      // Simulate curiosity engine
      simulateCuriosityEngine()
    } catch (error) {
      console.error("Error accessing microphone:", error)
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.pause()
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      setIsPaused(true)
    }
  }

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "paused") {
      mediaRecorderRef.current.resume()
      timerRef.current = setInterval(() => {
        setRecordingTime((prevTime) => prevTime + 1)
      }, 1000)
      setIsPaused(false)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" })
        // Here you would typically send the audio to your backend for processing
        console.log("Recording stopped, audio blob created:", audioBlob)

        // Reset recording state
        if (timerRef.current) {
          clearInterval(timerRef.current)
        }
        setIsRecording(false)
        setIsPaused(false)
        // Don't reset the time immediately so user can see final duration
      }
    }
  }

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const addBookmark = () => {
    console.log("Bookmark added at", formatTime(recordingTime))
    // In a real implementation, you would store this bookmark
  }

  const simulateLiveTranscription = () => {
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
        setLiveText((prev) => prev + (prev ? " " : "") + demoTexts[currentIndex])
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 3000)
  }

  const simulateAIInsights = () => {
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
        setAiInsights((prev) => [...prev, demoInsights[currentIndex]])
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 5000)
  }

  const simulateCuriosityEngine = () => {
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
  }

  const handleAnswerQuestion = (id: string, answer: string) => {
    setQuestions((prev) => prev.map((q) => (q.id === id ? { ...q, answered: true, answer } : q)))
  }

  return (
    <div className="p-4 max-w-7xl mx-auto">
      {/* Session Name */}
      <div className="mb-4">
        <label className="text-sm font-medium mb-1 block">Session Name</label>
        <Input
          placeholder="Enter session name..."
          value={sessionName}
          onChange={(e) => setSessionName(e.target.value)}
          className="w-full"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          {/* Recording Controls */}
          <Card>
            <CardContent className="p-4">
              <h2 className="text-lg font-medium mb-4">Recording Controls</h2>
              <div className="flex flex-wrap gap-2 mb-4">
                {!isRecording ? (
                  <Button onClick={startRecording} className="bg-destructive hover:bg-destructive/90">
                    <Mic className="h-4 w-4 mr-2" /> Record
                  </Button>
                ) : isPaused ? (
                  <Button onClick={resumeRecording} variant="outline">
                    <Play className="h-4 w-4 mr-2" /> Resume
                  </Button>
                ) : (
                  <Button onClick={pauseRecording} variant="outline">
                    <Pause className="h-4 w-4 mr-2" /> Pause
                  </Button>
                )}
                {isRecording && (
                  <Button variant="outline" onClick={stopRecording}>
                    <MicOff className="h-4 w-4 mr-2" /> Stop
                  </Button>
                )}
                <Button variant="outline" disabled={!isRecording}>
                  <RefreshCw className="h-4 w-4 mr-2" /> Mute
                </Button>
                <div className="ml-auto text-2xl font-mono flex items-center">{formatTime(recordingTime)}</div>
              </div>

              <div className="waveform-container mb-4">
                <div className="waveform">
                  {Array.from({ length: 50 }).map((_, i) => (
                    <div
                      key={i}
                      className="waveform-bar"
                      style={{
                        height: isRecording && !isPaused ? `${Math.floor(Math.random() * 60) + 10}%` : "10%",
                      }}
                    />
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Tools */}
          <Card>
            <CardContent className="p-4">
              <h2 className="text-lg font-medium mb-4">Analysis Tools</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Template</label>
                  <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select template" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full-analysis">Full Analysis</SelectItem>
                      <SelectItem value="meeting-summary">Meeting Summary</SelectItem>
                      <SelectItem value="interview">Interview Analysis</SelectItem>
                      <SelectItem value="lecture">Lecture Notes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Processing</label>
                  <Select value={processingMode} onValueChange={setProcessingMode}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select mode" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manual">Manual (F12)</SelectItem>
                      <SelectItem value="timed">Timed (30s)</SelectItem>
                      <SelectItem value="word-count">Word Count (100)</SelectItem>
                      <SelectItem value="silence">Silence Detection</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                <Button variant="secondary">
                  <RefreshCw className="h-4 w-4 mr-2" /> Process (F12)
                </Button>
                <Button variant="secondary">
                  <FileText className="h-4 w-4 mr-2" /> Full Analysis (F10)
                </Button>
                <Button variant="secondary">Deep Analysis</Button>
              </div>
            </CardContent>
          </Card>

          {/* Live Text */}
          <Card>
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-medium">Live Text</h2>
                <Button variant="outline" size="sm">
                  <Copy className="h-4 w-4 mr-2" /> Copy
                </Button>
              </div>
              <div className="min-h-[200px] border rounded-md p-4 bg-background mb-4">
                {isRecording && liveText ? (
                  <p>{liveText}</p>
                ) : isRecording ? (
                  <div className="flex items-center text-muted-foreground">
                    <span className="recording-dot"></span>
                    Listening...
                  </div>
                ) : (
                  <p className="text-muted-foreground">Start recording to see live transcription</p>
                )}
              </div>
              <div className="flex justify-between">
                <Button variant="outline">Edit Mode: Off</Button>
                <Button variant="outline">
                  <Save className="h-4 w-4 mr-2" /> Save Transcript
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Bookmarks & Voice Commands */}
          <Card>
            <CardContent className="p-4">
              <h2 className="text-lg font-medium mb-4">Bookmarks & Voice Commands</h2>
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={addBookmark} disabled={!isRecording}>
                  <Bookmark className="h-4 w-4 mr-2" /> Voice Commands
                </Button>
                <Button variant="outline" onClick={addBookmark} disabled={!isRecording}>
                  <Bookmark className="h-4 w-4 mr-2" /> Quick Mark (F8)
                </Button>
                <Button variant="outline" onClick={addBookmark} disabled={!isRecording}>
                  <Bookmark className="h-4 w-4 mr-2" /> Named Mark (F9)
                </Button>
                <Button variant="outline" onClick={addBookmark} disabled={!isRecording}>
                  <FileText className="h-4 w-4 mr-2" /> Full Analysis (F10)
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          {/* AI Tools */}
          <Card>
            <CardContent className="p-0">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="w-full rounded-none">
                  <TabsTrigger value="insights" className="flex-1">
                    AI Insights
                  </TabsTrigger>
                  <TabsTrigger value="curiosity" className="flex-1">
                    Curiosity
                  </TabsTrigger>
                  <TabsTrigger value="compass" className="flex-1">
                    Conversation Compass
                  </TabsTrigger>
                </TabsList>

                <div className="p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-sm font-medium">AI Insights</h3>
                    <Button variant="outline" size="sm">
                      <Copy className="h-4 w-4 mr-2" /> Copy
                    </Button>
                  </div>

                  <TabsContent value="insights" className="mt-0">
                    <div className="min-h-[400px] border rounded-md p-4 bg-background">
                      {aiInsights.length > 0 ? (
                        <div className="space-y-3">
                          {aiInsights.map((insight, index) => (
                            <div key={index} className="p-2 bg-muted rounded-md">
                              {insight}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-muted-foreground">
                          {isRecording
                            ? "Analyzing conversation for insights..."
                            : "Start recording to generate AI insights"}
                        </p>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="curiosity" className="mt-0">
                    <div className="min-h-[400px] border rounded-md p-4 bg-background">
                      {questions.length > 0 ? (
                        <div className="space-y-3">
                          {questions.map((question) => (
                            <div key={question.id} className="p-3 bg-muted rounded-md">
                              <p className="font-medium">{question.text}</p>
                              {question.answered ? (
                                <p className="mt-2 text-sm text-muted-foreground">Answer: {question.answer}</p>
                              ) : (
                                <div className="mt-2 flex gap-2">
                                  <Input
                                    placeholder="Type your answer..."
                                    className="text-sm"
                                    onKeyDown={(e) => {
                                      if (e.key === "Enter") {
                                        handleAnswerQuestion(question.id, (e.target as HTMLInputElement).value)
                                        ;(e.target as HTMLInputElement).value = ""
                                      }
                                    }}
                                  />
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-muted-foreground">
                          {isRecording
                            ? "Generating questions based on the conversation..."
                            : "Start recording to generate questions"}
                        </p>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="compass" className="mt-0">
                    <div className="min-h-[400px] border rounded-md p-4 bg-background">
                      {isRecording ? (
                        <div className="space-y-4">
                          <div className="p-3 bg-muted rounded-md">
                            <p className="font-medium">Conversation Structure</p>
                            <ul className="mt-2 space-y-2 pl-5 list-disc">
                              <li>
                                <span className="font-medium">Introduction</span>
                                <ul className="pl-5 mt-1 space-y-1 list-circle">
                                  <li>Welcome to weekly team meeting</li>
                                  <li>Q1 results discussion</li>
                                </ul>
                              </li>
                              <li>
                                <span className="font-medium">Key Metrics Review</span>
                                <ul className="pl-5 mt-1 space-y-1 list-circle">
                                  <li>Revenue growth: 15%</li>
                                  <li>Customer acquisition cost: -8%</li>
                                  <li>User retention: 85%</li>
                                </ul>
                              </li>
                              <li>
                                <span className="font-medium">Q2 Planning</span>
                              </li>
                            </ul>
                          </div>

                          <div className="p-3 bg-muted rounded-md">
                            <p className="font-medium">Suggested Responses</p>
                            <div className="mt-2 space-y-2">
                              <p className="text-sm">Ask about specific strategies that led to revenue growth</p>
                              <p className="text-sm">Inquire about regional performance differences</p>
                              <p className="text-sm">Suggest setting up weekly retention monitoring</p>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <p className="text-muted-foreground">
                          Start recording to visualize conversation flow and get suggestions
                        </p>
                      )}
                    </div>
                  </TabsContent>
                </div>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

