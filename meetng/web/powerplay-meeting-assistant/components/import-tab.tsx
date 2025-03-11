"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Progress } from "@/components/ui/progress"
import { Checkbox } from "@/components/ui/checkbox"
import { FolderOpen, File, X } from "lucide-react"

export default function ImportTab() {
  const [sourceType, setSourceType] = useState("file")
  const [service, setService] = useState("openai")
  const [path, setPath] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [enableTimestamps, setEnableTimestamps] = useState(true)
  const [enableSpeakerDetection, setEnableSpeakerDetection] = useState(true)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])

  const handleProcess = () => {
    if (!path) return

    setIsProcessing(true)
    setProgress(0)

    // Simulate processing
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsProcessing(false)
          return 100
        }
        return prev + 5
      })
    }, 500)

    // Add some demo files
    setSelectedFiles(["team_meeting_2023-03-15.mp3", "client_call_2023-03-15.mp3", "interview_2023-03-15.mp3"])
  }

  const handleCancel = () => {
    setIsProcessing(false)
    setProgress(0)
  }

  const removeFile = (file: string) => {
    setSelectedFiles(selectedFiles.filter((f) => f !== file))
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <Card className="p-6">
        <h2 className="text-xl font-bold mb-6">Import Audio Files</h2>

        {/* Source Selection */}
        <div className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Source</h3>
            <RadioGroup value={sourceType} onValueChange={setSourceType} className="flex gap-4">
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="file" id="file" />
                <Label htmlFor="file">Single File</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="folder" id="folder" />
                <Label htmlFor="folder">Folder</Label>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-2">
            <Label htmlFor="path">{sourceType === "file" ? "File Path" : "Folder Path"}</Label>
            <div className="flex gap-2">
              <Input
                id="path"
                value={path}
                onChange={(e) => setPath(e.target.value)}
                placeholder={sourceType === "file" ? "/path/to/audio.mp3" : "/path/to/folder"}
                className="flex-1"
              />
              <Button variant="outline" className="flex items-center gap-2">
                {sourceType === "file" ? <File className="h-4 w-4" /> : <FolderOpen className="h-4 w-4" />}
                <span>Select {sourceType === "file" ? "File" : "Folder"}</span>
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Transcription Service</h3>
              <RadioGroup value={service} onValueChange={setService} className="space-y-2">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="openai" id="openai" />
                  <Label htmlFor="openai">OpenAI Whisper</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="assemblyai" id="assemblyai" />
                  <Label htmlFor="assemblyai">AssemblyAI</Label>
                </div>
              </RadioGroup>

              <div className="space-y-2 mt-4">
                <Label htmlFor="model">Model</Label>
                <Select defaultValue={service === "openai" ? "whisper-1" : "default"}>
                  <SelectTrigger id="model">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {service === "openai" ? (
                      <>
                        <SelectItem value="whisper-1">Whisper-1</SelectItem>
                        <SelectItem value="whisper-large">Whisper Large</SelectItem>
                      </>
                    ) : (
                      <>
                        <SelectItem value="default">Default</SelectItem>
                        <SelectItem value="enhanced">Enhanced</SelectItem>
                      </>
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-medium">Features</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="timestamps">Include Timestamps</Label>
                  <Switch id="timestamps" checked={enableTimestamps} onCheckedChange={setEnableTimestamps} />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="speaker-detection">Speaker Detection</Label>
                  <Switch
                    id="speaker-detection"
                    checked={enableSpeakerDetection}
                    onCheckedChange={setEnableSpeakerDetection}
                  />
                </div>
              </div>

              <div className="space-y-2 mt-4">
                <Label htmlFor="naming">File Naming</Label>
                <Select defaultValue="original">
                  <SelectTrigger id="naming">
                    <SelectValue placeholder="Select naming convention" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="original">Original filename</SelectItem>
                    <SelectItem value="date">Date + Original filename</SelectItem>
                    <SelectItem value="custom">Custom pattern</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Progress Section */}
      <Card className="p-6">
        <h2 className="text-xl font-bold mb-6">Progress</h2>

        <div className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label>Status</Label>
              <span className="text-sm font-medium">
                {!isProcessing && progress === 0 && "Ready"}
                {isProcessing && "Processing..."}
                {!isProcessing && progress === 100 && "Complete"}
              </span>
            </div>
            <Progress value={progress} className="h-2" />
            {isProcessing && <p className="text-sm text-muted-foreground text-right">{progress}%</p>}
          </div>

          <div className="space-y-2">
            <Label>Files</Label>
            <div className="border rounded-md overflow-hidden">
              {selectedFiles.length > 0 ? (
                <div className="max-h-[200px] overflow-y-auto">
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 hover:bg-muted/50">
                      <div className="flex items-center gap-2">
                        <Checkbox id={`file-${index}`} />
                        <Label htmlFor={`file-${index}`} className="text-sm cursor-pointer">
                          {file}
                        </Label>
                      </div>
                      <Button variant="ghost" size="icon" onClick={() => removeFile(file)}>
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center text-muted-foreground">No files selected</div>
              )}
            </div>
          </div>

          <div className="flex justify-end gap-2">
            {isProcessing ? (
              <Button variant="destructive" onClick={handleCancel}>
                Cancel
              </Button>
            ) : (
              <Button onClick={handleProcess} disabled={!path}>
                Process
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}

