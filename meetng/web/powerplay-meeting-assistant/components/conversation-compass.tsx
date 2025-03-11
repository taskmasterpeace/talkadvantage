"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Settings, Target, Maximize2, Minimize2 } from "lucide-react"

interface ConversationCompassProps {
  hasContent: boolean
}

export default function ConversationCompass({ hasContent }: ConversationCompassProps) {
  const [mode, setMode] = useState("tracking")
  const [isFullscreen, setIsFullscreen] = useState(false)

  if (!hasContent) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <Target className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">Conversation Compass</h3>
        <p className="text-muted-foreground mb-4">
          Start recording to visualize conversation flow and get AI-powered guidance.
        </p>
        <Button variant="outline" disabled>
          Setup Compass
        </Button>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-2">
        <Tabs value={mode} onValueChange={setMode} className="w-auto">
          <TabsList className="grid w-[200px] grid-cols-2">
            <TabsTrigger value="tracking">Tracking</TabsTrigger>
            <TabsTrigger value="guided">Guided</TabsTrigger>
          </TabsList>
        </Tabs>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Settings className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsFullscreen(!isFullscreen)}>
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      <div className="flex-1 p-2 relative">
        {/* Tree visualization */}
        <svg width="100%" height="100%" viewBox="0 0 800 400" className="overflow-visible">
          {/* Central node */}
          <g transform="translate(400, 200)">
            <circle r="30" fill="#2563eb" />
            <text textAnchor="middle" fill="white" dy="5" fontSize="12">
              Meeting
            </text>

            {/* Branches */}
            <g>
              {/* Topic 1 */}
              <line x1="0" y1="0" x2="-150" y2="-100" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="-150" cy="-100" r="25" fill="#3b82f6" />
              <text x="-150" y="-100" textAnchor="middle" fill="white" dy="5" fontSize="10">
                Timeline
              </text>

              {/* Sub-branch 1 */}
              <line x1="-150" y1="-100" x2="-250" y2="-150" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="-250" cy="-150" r="20" fill="#60a5fa" />
              <text x="-250" y="-150" textAnchor="middle" fill="white" dy="4" fontSize="9">
                Delays
              </text>

              {/* Sub-branch 2 */}
              <line x1="-150" y1="-100" x2="-200" y2="-50" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="-200" cy="-50" r="20" fill="#60a5fa" />
              <text x="-200" y="-50" textAnchor="middle" fill="white" dy="4" fontSize="9">
                Follow-up
              </text>

              {/* Topic 2 */}
              <line x1="0" y1="0" x2="150" y2="-100" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="150" cy="-100" r="25" fill="#3b82f6" />
              <text x="150" y="-100" textAnchor="middle" fill="white" dy="5" fontSize="10">
                Resources
              </text>

              {/* Sub-branch 3 */}
              <line x1="150" y1="-100" x2="250" y2="-150" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="250" cy="-150" r="20" fill="#60a5fa" />
              <text x="250" y="-150" textAnchor="middle" fill="white" dy="4" fontSize="9">
                Allocation
              </text>

              {/* Topic 3 */}
              <line x1="0" y1="0" x2="0" y2="150" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="0" cy="150" r="25" fill="#3b82f6" />
              <text x="0" y="150" textAnchor="middle" fill="white" dy="5" fontSize="10">
                Features
              </text>

              {/* Sub-branch 4 */}
              <line x1="0" y1="150" x2="-100" y2="200" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="-100" cy="200" r="20" fill="#60a5fa" />
              <text x="-100" y="200" textAnchor="middle" fill="white" dy="4" fontSize="9">
                Client
              </text>

              {/* Sub-branch 5 */}
              <line x1="0" y1="150" x2="100" y2="200" stroke="#d1d5db" strokeWidth="2" />
              <circle cx="100" cy="200" r="20" fill="#60a5fa" />
              <text x="100" y="200" textAnchor="middle" fill="white" dy="4" fontSize="9">
                UX
              </text>
            </g>
          </g>
        </svg>

        {/* Minimap */}
        <div className="absolute bottom-2 right-2 w-[100px] h-[60px] border border-border bg-background/80 rounded-md p-1">
          <svg width="100%" height="100%" viewBox="0 0 800 400">
            <rect x="300" y="150" width="200" height="100" stroke="#2563eb" strokeWidth="2" fill="none" />
            <circle cx="400" cy="200" r="5" fill="#2563eb" />
            <circle cx="250" cy="100" r="3" fill="#3b82f6" />
            <circle cx="550" cy="100" r="3" fill="#3b82f6" />
            <circle cx="400" cy="350" r="3" fill="#3b82f6" />
          </svg>
        </div>
      </div>

      {mode === "guided" && (
        <Card className="m-2 p-2">
          <h4 className="text-sm font-medium mb-2">Suggested Responses</h4>
          <div className="space-y-2">
            <div className="text-xs p-2 bg-muted rounded-md cursor-pointer hover:bg-muted/70">
              "Let's discuss how we can adjust the timeline to accommodate the new features."
            </div>
            <div className="text-xs p-2 bg-muted rounded-md cursor-pointer hover:bg-muted/70">
              "What specific resources do we need to allocate to meet the client's expectations?"
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

