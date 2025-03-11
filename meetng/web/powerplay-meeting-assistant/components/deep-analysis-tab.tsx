"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { X, Search, ChevronLeft, ChevronRight, Download, Trash2, Plus, BarChart2, MessageSquare } from "lucide-react"
import MediaPlayer from "./media-player"

export default function DeepAnalysisTab() {
  const [selectedTranscripts, setSelectedTranscripts] = useState([
    { id: 1, name: "Team Meeting - March 15", date: "2023-03-15" },
    { id: 2, name: "Client Call - Project Kickoff", date: "2023-03-15" },
  ])
  const [autoScroll, setAutoScroll] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [visualizationType, setVisualizationType] = useState("wordcloud")

  const demoTranscripts = [
    { id: 1, name: "Team Meeting - March 15", date: "2023-03-15", selected: true },
    { id: 2, name: "Client Call - Project Kickoff", date: "2023-03-15", selected: true },
    { id: 3, name: "Interview - Senior Developer", date: "2023-03-15", selected: false },
    { id: 4, name: "Product Planning", date: "2023-03-14", selected: false },
    { id: 5, name: "Weekly Standup", date: "2023-03-13", selected: false },
  ]

  const demoTranscriptText = `
[00:01:15] John: I think we should focus on the user experience first. The client mentioned that was their top priority.

[00:01:32] Sarah: Agreed. We've received feedback that the current interface is confusing for new users.

[00:01:45] Michael: What about the timeline for the project? We're already behind schedule on the backend development.

[00:02:10] John: We need to allocate more resources to the development team. Maybe we can pull someone from the other project?

[00:02:30] Sarah: The client requested additional features yesterday. That's going to impact our timeline as well.

[00:02:45] Michael: Let's schedule a follow-up meeting next week to reassess our progress and adjust the timeline if needed.

[00:03:10] John: Good idea. I'll send out a calendar invite after this call.
  `

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Panel */}
      <div className="space-y-4">
        {/* Transcript Selection */}
        <Card>
          <div className="bg-muted p-2 flex items-center justify-between">
            <h3 className="font-medium">Selected Transcripts</h3>
            <Button variant="ghost" size="icon">
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="p-2 max-h-[150px] overflow-y-auto">
            {selectedTranscripts.length > 0 ? (
              <div className="space-y-2">
                {selectedTranscripts.map((transcript) => (
                  <div key={transcript.id} className="flex items-center justify-between p-2 bg-muted/30 rounded-md">
                    <div>
                      <div className="font-medium text-sm">{transcript.name}</div>
                      <div className="text-xs text-muted-foreground">{transcript.date}</div>
                    </div>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-20 text-muted-foreground">No transcripts selected</div>
            )}
          </div>
        </Card>

        {/* Media Player */}
        <Card>
          <div className="bg-muted p-2">
            <h3 className="font-medium">Media Player</h3>
          </div>
          <div className="p-4">
            <MediaPlayer showBookmarks={true} />
          </div>
        </Card>

        {/* Transcript Viewer */}
        <Card className="overflow-hidden">
          <div className="bg-muted p-2 flex items-center justify-between">
            <h3 className="font-medium">Transcript</h3>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search transcript..."
                  className="pl-8 h-9 w-[200px]"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="flex items-center gap-1">
                <Button variant="ghost" size="icon" className="h-9 w-9" disabled={!searchQuery}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="h-9 w-9" disabled={!searchQuery}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="auto-scroll"
                  checked={autoScroll}
                  onCheckedChange={(checked) => setAutoScroll(checked as boolean)}
                />
                <Label htmlFor="auto-scroll" className="text-sm">
                  Auto-scroll
                </Label>
              </div>
            </div>
          </div>
          <div className="p-4 h-[300px] overflow-y-auto font-mono text-sm whitespace-pre-wrap">
            {demoTranscriptText}
          </div>
        </Card>
      </div>

      {/* Right Panel */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium">Analysis</h3>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Analysis
          </Button>
        </div>

        <Tabs defaultValue="insights">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="insights">Transcript Insights</TabsTrigger>
            <TabsTrigger value="visualizations">Visualizations</TabsTrigger>
            <TabsTrigger value="chat">Analysis Chat</TabsTrigger>
          </TabsList>

          <TabsContent value="insights" className="space-y-4 mt-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  Select All
                </Button>
                <Button variant="outline" size="sm">
                  Clear
                </Button>
              </div>
              <Button>Analyze Selected</Button>
            </div>

            <Card className="overflow-hidden">
              <div className="p-2 max-h-[500px] overflow-y-auto">
                <div className="space-y-2">
                  {demoTranscripts.map((transcript) => (
                    <div key={transcript.id} className="flex items-center gap-2 p-2 hover:bg-muted/50 rounded-md">
                      <Checkbox checked={transcript.selected} />
                      <div>
                        <div className="font-medium text-sm">{transcript.name}</div>
                        <div className="text-xs text-muted-foreground">{transcript.date}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="visualizations" className="space-y-4 mt-4">
            <Card className="p-4">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2">
                  <Label htmlFor="viz-type">Visualization Type</Label>
                  <Select value={visualizationType} onValueChange={setVisualizationType}>
                    <SelectTrigger id="viz-type" className="w-[180px]">
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="wordcloud">Word Cloud</SelectItem>
                      <SelectItem value="topwords">Top Words</SelectItem>
                      <SelectItem value="timeline">Timeline</SelectItem>
                      <SelectItem value="sentiment">Sentiment Analysis</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button>Generate</Button>
              </div>

              <div className="h-[300px] bg-muted/30 rounded-md flex items-center justify-center">
                {visualizationType === "wordcloud" ? (
                  <div className="text-center p-4">
                    <div className="font-bold text-3xl text-primary">project</div>
                    <div className="font-bold text-2xl text-primary/80">timeline</div>
                    <div className="font-bold text-xl text-primary/70">client</div>
                    <div className="font-bold text-xl text-primary/60">features</div>
                    <div className="text-lg text-primary/50">resources</div>
                    <div className="text-lg text-primary/50">development</div>
                    <div className="text-md text-primary/40">meeting</div>
                    <div className="text-md text-primary/40">interface</div>
                    <div className="text-sm text-primary/30">experience</div>
                    <div className="text-sm text-primary/30">feedback</div>
                  </div>
                ) : (
                  <div className="text-muted-foreground">
                    <BarChart2 className="h-12 w-12 mx-auto mb-2" />
                    <p>Generate visualization to see results</p>
                  </div>
                )}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="chat" className="space-y-4 mt-4">
            <Card className="overflow-hidden">
              <div className="bg-muted p-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  <h3 className="font-medium">Analysis Chat</h3>
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="p-4 h-[300px] overflow-y-auto space-y-4">
                <div className="bg-primary/10 rounded-lg p-3 max-w-[80%]">
                  <p className="text-sm font-medium mb-1">You</p>
                  <p className="text-sm">What are the main topics discussed in these transcripts?</p>
                </div>

                <div className="bg-muted rounded-lg p-3 max-w-[80%] ml-auto">
                  <p className="text-sm font-medium mb-1">AI Assistant</p>
                  <p className="text-sm">Based on the transcripts, the main topics discussed are:</p>
                  <ol className="text-sm list-decimal pl-5 mt-2">
                    <li>User experience concerns and prioritization</li>
                    <li>Project timeline challenges and delays</li>
                    <li>Resource allocation for the development team</li>
                    <li>Client requests for additional features</li>
                    <li>Follow-up meeting planning</li>
                  </ol>
                  <p className="text-sm mt-2">
                    The conversation primarily revolves around project management concerns, with team members discussing
                    how to balance client requests with existing timelines and resources.
                  </p>
                </div>
              </div>

              <div className="p-2 border-t">
                <div className="flex items-center gap-2">
                  <Input placeholder="Ask a question about the transcripts..." />
                  <Button>Send</Button>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

