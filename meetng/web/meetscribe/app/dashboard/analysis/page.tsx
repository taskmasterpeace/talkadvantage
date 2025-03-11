"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { FileText, MessageSquare, BarChart2, PieChart, Send } from "lucide-react"

export default function AnalysisPage() {
  const [selectedTranscripts, setSelectedTranscripts] = useState<string[]>(["1", "3"])
  const [chatMessage, setChatMessage] = useState("")

  const handleTranscriptToggle = (id: string) => {
    setSelectedTranscripts((prev) => (prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]))
  }

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Deep Analysis</h1>
        <Button>
          <FileText className="h-4 w-4 mr-2" /> Import Transcripts
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Available Transcripts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockTranscripts.map((transcript) => (
                  <div key={transcript.id} className="flex items-start space-x-2">
                    <Checkbox
                      id={`transcript-${transcript.id}`}
                      checked={selectedTranscripts.includes(transcript.id)}
                      onCheckedChange={() => handleTranscriptToggle(transcript.id)}
                    />
                    <div className="grid gap-1.5">
                      <label
                        htmlFor={`transcript-${transcript.id}`}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        {transcript.title}
                      </label>
                      <p className="text-xs text-muted-foreground">
                        {transcript.date} • {transcript.duration}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Visualizations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button variant="outline" className="w-full justify-start">
                  <BarChart2 className="h-4 w-4 mr-2" />
                  Topic Distribution
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <PieChart className="h-4 w-4 mr-2" />
                  Speaker Time Analysis
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <BarChart2 className="h-4 w-4 mr-2" />
                  Sentiment Over Time
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <PieChart className="h-4 w-4 mr-2" />
                  Key Terms Frequency
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2 space-y-4">
          <Tabs defaultValue="chat">
            <TabsList className="w-full">
              <TabsTrigger value="chat" className="flex-1">
                <MessageSquare className="h-4 w-4 mr-2" />
                Contextual Chat
              </TabsTrigger>
              <TabsTrigger value="transcripts" className="flex-1">
                <FileText className="h-4 w-4 mr-2" />
                Transcripts
              </TabsTrigger>
              <TabsTrigger value="insights" className="flex-1">
                <BarChart2 className="h-4 w-4 mr-2" />
                AI Insights
              </TabsTrigger>
            </TabsList>

            <TabsContent value="chat" className="mt-4 space-y-4">
              <Card className="border-muted">
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-sm font-medium">AI Assistant</p>
                      <p className="mt-1">
                        I've analyzed the selected transcripts. The main topics discussed were quarterly results,
                        customer acquisition strategies, and retention plans. What specific insights would you like to
                        explore?
                      </p>
                    </div>

                    <div className="bg-primary/10 p-3 rounded-lg ml-8">
                      <p className="text-sm font-medium">You</p>
                      <p className="mt-1">What were the key metrics mentioned across these meetings?</p>
                    </div>

                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-sm font-medium">AI Assistant</p>
                      <p className="mt-1">The key metrics mentioned across the selected meetings were:</p>
                      <ul className="list-disc pl-5 mt-2 space-y-1">
                        <li>Revenue growth: 15% (exceeded target of 12%)</li>
                        <li>Customer acquisition cost: Decreased by 8%</li>
                        <li>User retention rate: Currently at 85%, with a Q2 target of 90%</li>
                        <li>Customer satisfaction score: 4.2/5</li>
                        <li>Monthly active users: Increased by 12% to 1.2 million</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="flex gap-2">
                <Input
                  placeholder="Ask a question about the transcripts..."
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                />
                <Button>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="transcripts" className="mt-4">
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    {selectedTranscripts.length > 0 ? (
                      mockTranscripts
                        .filter((t) => selectedTranscripts.includes(t.id))
                        .map((transcript) => (
                          <div key={transcript.id} className="space-y-2">
                            <h3 className="font-medium">{transcript.title}</h3>
                            <p className="text-sm text-muted-foreground">
                              {transcript.date} • {transcript.duration}
                            </p>
                            <div className="border-l-2 border-primary pl-4 mt-2">
                              <p className="whitespace-pre-line">{transcript.content}</p>
                            </div>
                          </div>
                        ))
                    ) : (
                      <p className="text-center text-muted-foreground">
                        Select transcripts from the sidebar to view them here
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="insights" className="mt-4">
              <Card>
                <CardContent className="p-6">
                  {selectedTranscripts.length > 0 ? (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-medium mb-2">Key Topics</h3>
                        <div className="flex flex-wrap gap-2">
                          {[
                            "Revenue Growth",
                            "Customer Acquisition",
                            "User Retention",
                            "Q1 Results",
                            "Marketing Strategy",
                            "Product Development",
                          ].map((topic) => (
                            <div key={topic} className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm">
                              {topic}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium mb-2">Action Items Detected</h3>
                        <ul className="list-disc pl-5 space-y-2">
                          <li>Improve user retention rate to 90% by end of Q2</li>
                          <li>Investigate lower customer acquisition costs in email marketing channel</li>
                          <li>Schedule follow-up meeting to discuss product roadmap</li>
                          <li>Prepare detailed analysis of regional performance differences</li>
                        </ul>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium mb-2">Questions Raised</h3>
                        <ul className="list-disc pl-5 space-y-2">
                          <li>How can we further reduce customer acquisition costs?</li>
                          <li>What specific strategies led to the 15% revenue growth?</li>
                          <li>Are there seasonal patterns affecting our Q1 results?</li>
                          <li>Which features would have the biggest impact on retention?</li>
                        </ul>
                      </div>

                      <div>
                        <h3 className="text-lg font-medium mb-2">Sentiment Analysis</h3>
                        <div className="flex items-center gap-4">
                          <div className="w-full bg-muted rounded-full h-4">
                            <div className="bg-success h-4 rounded-full" style={{ width: "75%" }}></div>
                          </div>
                          <span className="text-sm font-medium">75% Positive</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-center text-muted-foreground">
                      Select transcripts from the sidebar to view AI insights
                    </p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

interface Transcript {
  id: string
  title: string
  date: string
  duration: string
  content: string
}

const mockTranscripts: Transcript[] = [
  {
    id: "1",
    title: "Weekly Team Meeting",
    date: "Mar 6, 2025",
    duration: "45:12",
    content: `Team Lead: Hello everyone, welcome to our weekly team meeting. Today we'll be discussing the Q1 results and our plans for Q2.

Finance: I'll start with the revenue numbers. We've seen a 15% growth compared to the previous quarter, which exceeded our target of 12%.

Marketing: That's great news. On our end, customer acquisition cost decreased by 8%, which is a positive trend we want to continue.

Product: Our user retention rate remained stable at 85%, but we're aiming to improve this to 90% in Q2.

Team Lead: Excellent. Let's discuss specific strategies for Q2 to build on these results.`,
  },
  {
    id: "2",
    title: "Client Interview - Project Alpha",
    date: "Mar 6, 2025",
    duration: "32:47",
    content: `Interviewer: Thank you for joining us today to discuss Project Alpha. Could you tell us about your experience with the current system?

Client: The current system is quite outdated. We spend too much time on manual processes that could be automated.

Interviewer: What specific features would you like to see in the new system?

Client: Definitely better reporting capabilities, integration with our CRM, and a more intuitive user interface.

Interviewer: How would you prioritize these features?

Client: The reporting is most critical, followed by the CRM integration. The UI improvements could come later if needed.`,
  },
  {
    id: "3",
    title: "Product Planning Session",
    date: "Mar 4, 2025",
    duration: "1:12:33",
    content: `Product Manager: Today we need to finalize the feature roadmap for the next quarter.

UX Designer: Based on user research, the dashboard redesign should be our top priority. Users are struggling with the current layout.

Developer: I agree, but we also need to address the performance issues. Page load times have increased by 30% in the last month.

Product Manager: Good point. Let's prioritize both. We'll start with the performance optimization and then move to the dashboard redesign.

Marketing: We should also consider adding the social sharing feature that's been requested by several enterprise customers.

Product Manager: Let's add that to the backlog and revisit after we complete the critical items.`,
  },
  {
    id: "4",
    title: "Marketing Strategy Discussion",
    date: "Mar 2, 2025",
    duration: "28:05",
    content: `Marketing Lead: Let's review our Q1 campaign performance and plan for Q2.

Social Media Manager: Our LinkedIn campaigns performed exceptionally well, with a 22% increase in qualified leads.

Content Strategist: The blog content focused on industry trends generated the most engagement, with an average time on page of 4.5 minutes.

Marketing Lead: Great insights. For Q2, let's double down on LinkedIn and increase our industry analysis content.

Email Marketing: We should also note that our email open rates improved to 28% after we implemented the new segmentation strategy.

Marketing Lead: Excellent. Let's continue refining our segmentation and personalization efforts in Q2.`,
  },
]

