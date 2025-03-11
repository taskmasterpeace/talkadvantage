"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import {
  Bookmark,
  Edit,
  Copy,
  Play,
  Pause,
  Square,
  Mic,
  MicOff,
  RefreshCw,
  X,
  Clock,
  MessageSquare,
  HelpCircle,
  Save,
} from "lucide-react"
import AudioVisualizer from "./audio-visualizer"
import ConversationCompass from "./conversation-compass"
import CuriosityEngine from "./curiosity-engine"

export default function RecordingTab() {
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [isMuted, setIsMuted] = useState(false)
  const [sessionName, setSessionName] = useState("New Meeting")
  const [liveText, setLiveText] = useState("")
  const [editMode, setEditMode] = useState(false)

  // Simulate recording timer
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1)
        // Simulate live transcription
        if (recordingTime % 5 === 0) {
          setLiveText((prev) => prev + " " + getDemoText())
        }
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isRecording, recordingTime])

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    return [h, m, s].map((v) => v.toString().padStart(2, "0")).join(":")
  }

  const getDemoText = () => {
    const phrases = [
      "I think we should focus on the user experience first.",
      "What about the timeline for the project?",
      "We need to allocate more resources to the development team.",
      "The client requested additional features yesterday.",
      "Let's schedule a follow-up meeting next week.",
    ]
    return phrases[Math.floor(Math.random() * phrases.length)]
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    if (!isRecording) {
      // Reset if starting a new recording
      setRecordingTime(0)
      setLiveText("")
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Session Name Field */}
        <div className="flex items-center gap-2">
          <Input value={sessionName} onChange={(e) => setSessionName(e.target.value)} className="text-lg font-medium" />
          <Button variant="ghost" size="icon">
            <Edit className="h-4 w-4" />
          </Button>
        </div>

        {/* Recording Controls Panel */}
        <Card className="p-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                variant={isRecording ? "destructive" : "default"}
                size="icon"
                onClick={toggleRecording}
                className="h-10 w-10 rounded-full"
              >
                {isRecording ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
              </Button>
              <Button variant="outline" size="icon" disabled={!isRecording} className="h-10 w-10 rounded-full">
                <Square className="h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setIsMuted(!isMuted)}
                className={`h-10 w-10 rounded-full ${isMuted ? "bg-red-100 text-red-500" : ""}`}
              >
                {isMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </Button>
            </div>
            <div className="text-xl font-mono">{formatTime(recordingTime)}</div>
            <div className="w-24 h-10">
              <AudioVisualizer isActive={isRecording && !isMuted} />
            </div>
          </div>
        </Card>

        {/* Analysis Tools Panel */}
        <Card className="p-2">
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Select defaultValue="default">
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Template" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Default Template</SelectItem>
                    <SelectItem value="meeting">Meeting Summary</SelectItem>
                    <SelectItem value="interview">Interview Analysis</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="ghost" size="icon">
                  <Edit className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Select defaultValue="manual">
                  <SelectTrigger className="w-[140px]">
                    <SelectValue placeholder="Processing" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="manual">Manual</SelectItem>
                    <SelectItem value="time">Time (5 min)</SelectItem>
                    <SelectItem value="words">Words (500)</SelectItem>
                    <SelectItem value="silence">Silence (2s)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled={!liveText}>
                  Process
                </Button>
                <Button variant="outline" size="sm" disabled={!liveText}>
                  Full Analysis
                </Button>
                <Button variant="outline" size="sm" disabled={!liveText}>
                  Deep Analysis
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon">
                  <RefreshCw className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Panel: Live Text */}
        <Card className="overflow-hidden">
          <div className="bg-muted p-2 flex items-center justify-between">
            <h3 className="font-medium">Live Text</h3>
            <div className="flex items-center gap-2">
              <Select defaultValue="default">
                <SelectTrigger className="w-[100px] h-8">
                  <SelectValue placeholder="Font" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default</SelectItem>
                  <SelectItem value="large">Large</SelectItem>
                  <SelectItem value="small">Small</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="p-4 h-[400px] overflow-y-auto">
            {liveText ? (
              <div className="space-y-4">
                {liveText
                  .split(".")
                  .filter(Boolean)
                  .map((sentence, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <span className="text-xs text-muted-foreground font-mono mt-1">{formatTime(idx * 5)}</span>
                      <p>{sentence.trim()}.</p>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                {isRecording ? "Waiting for speech..." : "Start recording to see transcription"}
              </div>
            )}
          </div>
        </Card>

        {/* Right Panel: Tabbed Interface */}
        <Card className="overflow-hidden">
          <Tabs defaultValue="insights">
            <div className="bg-muted p-2">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="insights">AI Insights</TabsTrigger>
                <TabsTrigger value="curiosity">Curiosity</TabsTrigger>
                <TabsTrigger value="compass">Conversation Compass</TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="insights" className="p-4 h-[400px] overflow-y-auto">
              {liveText ? (
                <div className="prose prose-sm max-w-none">
                  <h3>Meeting Summary</h3>
                  <p>The team is discussing project timelines and resource allocation. Key points:</p>
                  <ul>
                    <li>Focus on user experience as a priority</li>
                    <li>Timeline concerns have been raised</li>
                    <li>Development team needs additional resources</li>
                    <li>Client has requested new features</li>
                    <li>Follow-up meeting scheduled for next week</li>
                  </ul>
                  <h4>Action Items</h4>
                  <ul>
                    <li>Review resource allocation plan</li>
                    <li>Prepare timeline adjustment proposal</li>
                    <li>Document new feature requests</li>
                  </ul>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  No insights available yet
                </div>
              )}
            </TabsContent>

            <TabsContent value="curiosity" className="h-[400px] overflow-y-auto">
              <CuriosityEngine hasContent={!!liveText} />
            </TabsContent>

            <TabsContent value="compass" className="h-[400px] overflow-y-auto">
              <ConversationCompass hasContent={!!liveText} />
            </TabsContent>
          </Tabs>
        </Card>
      </div>

      {/* Bottom Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch id="edit-mode" checked={editMode} onCheckedChange={setEditMode} />
            <Label htmlFor="edit-mode">Edit Mode</Label>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" disabled={!liveText}>
            <Save className="h-4 w-4 mr-2" />
            Save Transcript
          </Button>
          <Button variant="outline" disabled={!liveText}>
            <Save className="h-4 w-4 mr-2" />
            Save Analysis
          </Button>
        </div>
      </div>

      {/* Bookmark Panel */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium">Bookmarks</h3>
          <Button variant="outline" size="sm">
            <MessageSquare className="h-4 w-4 mr-2" />
            Voice Commands
          </Button>
        </div>
        <div className="flex items-center gap-2 mb-4">
          <Button variant="outline" disabled={!isRecording}>
            <Bookmark className="h-4 w-4 mr-2" />
            Quick Bookmark (F8)
          </Button>
          <Button variant="outline" disabled={!isRecording}>
            <Bookmark className="h-4 w-4 mr-2" />
            Named Bookmark (F9)
          </Button>
          <Button variant="outline" disabled={!isRecording}>
            <HelpCircle className="h-4 w-4 mr-2" />
            Full Analysis (F10)
          </Button>
        </div>
        <div className="space-y-2">
          {recordingTime > 30 ? (
            <>
              <div className="flex items-center justify-between p-2 bg-muted rounded-md">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="font-mono text-sm">{formatTime(10)}</span>
                  <span className="font-medium">Timeline discussion</span>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Play className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center justify-between p-2 bg-muted rounded-md">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="font-mono text-sm">{formatTime(25)}</span>
                  <span className="font-medium">Resource allocation</span>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Play className="h-4 w-4" />
                </Button>
              </div>
            </>
          ) : (
            <div className="text-center text-muted-foreground py-4">No bookmarks yet</div>
          )}
        </div>
      </Card>
    </div>
  )
}

