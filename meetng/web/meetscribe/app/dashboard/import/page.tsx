"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Upload, FileText, FolderOpen, X, Check } from "lucide-react"

export default function ImportPage() {
  const [importType, setImportType] = useState<"file" | "folder">("file")
  const [transcriptionService, setTranscriptionService] = useState("whisper")
  const [model, setModel] = useState("whisper-large-v3")
  const [enableTimestamps, setEnableTimestamps] = useState(true)
  const [enableSpeakerDetection, setEnableSpeakerDetection] = useState(true)
  const [enableChapters, setEnableChapters] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])

  const handleStartImport = () => {
    setIsProcessing(true)
    setProgress(0)

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsProcessing(false)
          return 100
        }
        return prev + 10
      })
    }, 800)
  }

  const handleCancel = () => {
    setIsProcessing(false)
    setProgress(0)
  }

  const handleFileSelect = () => {
    // Simulate file selection
    setSelectedFiles(["interview_march_10.mp3", "team_meeting_march_12.wav"])
  }

  const handleFolderSelect = () => {
    // Simulate folder selection
    setSelectedFiles([
      "recordings/interview_march_10.mp3",
      "recordings/team_meeting_march_12.wav",
      "recordings/client_call_march_15.m4a",
    ])
  }

  const removeFile = (file: string) => {
    setSelectedFiles((prev) => prev.filter((f) => f !== file))
  }

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Import Audio</h1>
      </div>

      <Tabs defaultValue="import" className="space-y-4">
        <TabsList>
          <TabsTrigger value="import">Import Settings</TabsTrigger>
          <TabsTrigger value="api">API Configuration</TabsTrigger>
        </TabsList>

        <TabsContent value="import">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Source Selection</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="flex gap-4">
                    <Button
                      variant={importType === "file" ? "default" : "outline"}
                      onClick={() => setImportType("file")}
                      className="flex-1"
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Single File
                    </Button>
                    <Button
                      variant={importType === "folder" ? "default" : "outline"}
                      onClick={() => setImportType("folder")}
                      className="flex-1"
                    >
                      <FolderOpen className="h-4 w-4 mr-2" />
                      Folder
                    </Button>
                  </div>

                  <div>
                    <Button
                      variant="outline"
                      className="w-full h-32 border-dashed"
                      onClick={importType === "file" ? handleFileSelect : handleFolderSelect}
                    >
                      <div className="flex flex-col items-center">
                        <Upload className="h-8 w-8 mb-2 text-muted-foreground" />
                        <span>{importType === "file" ? "Click to select audio file" : "Click to select folder"}</span>
                        <span className="text-xs text-muted-foreground mt-1">Supports MP3, WAV, M4A</span>
                      </div>
                    </Button>
                  </div>

                  {selectedFiles.length > 0 && (
                    <div className="space-y-2">
                      <h3 className="text-sm font-medium">Selected {selectedFiles.length} file(s):</h3>
                      {selectedFiles.map((file) => (
                        <div key={file} className="flex items-center justify-between bg-muted p-2 rounded-md">
                          <span className="text-sm truncate">{file}</span>
                          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => removeFile(file)}>
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Transcription Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="space-y-2">
                    <Label>Transcription Service</Label>
                    <Select value={transcriptionService} onValueChange={setTranscriptionService}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select service" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="whisper">OpenAI Whisper</SelectItem>
                        <SelectItem value="assembly">AssemblyAI</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Model</Label>
                    <Select value={model} onValueChange={setModel}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select model" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="whisper-large-v3">Whisper Large v3</SelectItem>
                        <SelectItem value="whisper-medium">Whisper Medium</SelectItem>
                        <SelectItem value="whisper-small">Whisper Small</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-sm font-medium">Features</h3>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="timestamps" className="cursor-pointer">
                        Enable Timestamps
                      </Label>
                      <Switch id="timestamps" checked={enableTimestamps} onCheckedChange={setEnableTimestamps} />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="speaker-detection" className="cursor-pointer">
                        Speaker Detection
                      </Label>
                      <Switch
                        id="speaker-detection"
                        checked={enableSpeakerDetection}
                        onCheckedChange={setEnableSpeakerDetection}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <Label htmlFor="chapters" className="cursor-pointer">
                        Auto Chapters
                      </Label>
                      <Switch id="chapters" checked={enableChapters} onCheckedChange={setEnableChapters} />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Description (Optional)</Label>
                    <Textarea placeholder="Add notes about this import..." />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="mt-4">
            <CardContent className="pt-6">
              {isProcessing ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Processing {selectedFiles.length} file(s)</h3>
                      <p className="text-sm text-muted-foreground">
                        {progress < 100
                          ? `Transcribing ${Math.ceil((progress / 100) * selectedFiles.length)} of ${selectedFiles.length}`
                          : "Transcription complete!"}
                      </p>
                    </div>
                    <Button variant="outline" onClick={handleCancel} disabled={progress >= 100}>
                      {progress >= 100 ? (
                        <>
                          <Check className="h-4 w-4 mr-2" />
                          Done
                        </>
                      ) : (
                        "Cancel"
                      )}
                    </Button>
                  </div>
                  <Progress value={progress} className="h-2" />
                </div>
              ) : (
                <div className="flex justify-end gap-4">
                  <Button variant="outline">Reset</Button>
                  <Button onClick={handleStartImport} disabled={selectedFiles.length === 0}>
                    Start Import
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api">
          <Card>
            <CardHeader>
              <CardTitle>API Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label>OpenAI API Key</Label>
                  <Input type="password" placeholder="sk-..." />
                  <p className="text-xs text-muted-foreground">
                    Required for using OpenAI Whisper transcription service
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>AssemblyAI API Key</Label>
                  <Input type="password" placeholder="assembly-..." />
                  <p className="text-xs text-muted-foreground">Required for using AssemblyAI transcription service</p>
                </div>

                <Button>Save API Keys</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

