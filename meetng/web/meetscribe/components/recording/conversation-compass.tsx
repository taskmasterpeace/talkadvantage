"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface ConversationCompassProps {
  isRecording: boolean
}

interface ConversationNode {
  id: string
  text: string
  speaker: string
  children: ConversationNode[]
}

export function ConversationCompass({ isRecording }: ConversationCompassProps) {
  const [activeMode, setActiveMode] = useState<"passive" | "active">("passive")
  const [conversationTree, setConversationTree] = useState<ConversationNode | null>(null)
  const [suggestions, setSuggestions] = useState<string[]>([])

  useEffect(() => {
    if (!isRecording) return

    // Simulate conversation tree building during recording
    setTimeout(() => {
      setConversationTree({
        id: "root",
        text: "Weekly Team Meeting",
        speaker: "Moderator",
        children: [
          {
            id: "node-1",
            text: "Q1 Results Discussion",
            speaker: "Team Lead",
            children: [
              {
                id: "node-1-1",
                text: "Revenue grew by 15%",
                speaker: "Finance",
                children: [],
              },
              {
                id: "node-1-2",
                text: "Customer acquisition cost decreased by 8%",
                speaker: "Marketing",
                children: [],
              },
            ],
          },
          {
            id: "node-2",
            text: "Q2 Planning",
            speaker: "Team Lead",
            children: [
              {
                id: "node-2-1",
                text: "Improve user retention to 90%",
                speaker: "Product",
                children: [],
              },
            ],
          },
        ],
      })

      setSuggestions([
        "Ask about specific strategies that led to revenue growth",
        "Discuss regional performance differences",
        "Explore customer feedback trends from Q1",
        "Suggest setting up weekly retention monitoring",
      ])
    }, 4000)

    return () => {
      // Cleanup if needed
    }
  }, [isRecording])

  return (
    <div className="space-y-4">
      <Tabs value={activeMode} onValueChange={(v) => setActiveMode(v as "passive" | "active")}>
        <TabsList className="w-full">
          <TabsTrigger value="passive" className="flex-1">
            Passive
          </TabsTrigger>
          <TabsTrigger value="active" className="flex-1">
            Active Guidance
          </TabsTrigger>
        </TabsList>

        <TabsContent value="passive" className="mt-4">
          {conversationTree ? (
            <div className="space-y-2">
              <p className="text-sm font-medium">Conversation Structure:</p>
              <div className="border rounded-md p-3 text-sm">
                <div className="font-medium">{conversationTree.text}</div>
                <ul className="ml-4 mt-2 space-y-2">
                  {conversationTree.children.map((node) => (
                    <li key={node.id}>
                      <div className="font-medium">
                        {node.text} <span className="text-muted-foreground">({node.speaker})</span>
                      </div>
                      {node.children.length > 0 && (
                        <ul className="ml-4 mt-1 space-y-1">
                          {node.children.map((childNode) => (
                            <li key={childNode.id}>
                              {childNode.text} <span className="text-muted-foreground">({childNode.speaker})</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">
              {isRecording ? "Building conversation structure..." : "Start recording to visualize conversation"}
            </p>
          )}
        </TabsContent>

        <TabsContent value="active" className="mt-4">
          {suggestions.length > 0 ? (
            <div className="space-y-3">
              <p className="text-sm font-medium">Suggested Responses:</p>
              {suggestions.map((suggestion, index) => (
                <Card key={index}>
                  <CardContent className="p-3 text-sm">
                    {suggestion}
                    <div className="mt-2">
                      <Button size="sm" variant="outline" className="text-xs">
                        Use This
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">
              {isRecording
                ? "Analyzing conversation to provide guidance..."
                : "Start recording to receive conversation suggestions"}
            </p>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

