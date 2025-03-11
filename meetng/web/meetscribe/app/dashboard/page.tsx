import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Clock, Calendar, FileText, BarChart } from "lucide-react"
import Link from "next/link"

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link href="/dashboard/record">
          <Button>New Recording</Button>
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Recordings</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">+2 from last week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Recording Hours</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12.5</div>
            <p className="text-xs text-muted-foreground">8.5 hours remaining</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Transcribed</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18</div>
            <p className="text-xs text-muted-foreground">75% of recordings</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">AI Analyses</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">15</div>
            <p className="text-xs text-muted-foreground">62% of recordings</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="recent">
        <TabsList>
          <TabsTrigger value="recent">Recent Recordings</TabsTrigger>
          <TabsTrigger value="favorites">Favorites</TabsTrigger>
          <TabsTrigger value="shared">Shared With Me</TabsTrigger>
        </TabsList>
        <TabsContent value="recent" className="mt-6">
          <div className="grid gap-4">
            {recentRecordings.map((recording) => (
              <RecordingItem key={recording.id} recording={recording} />
            ))}
          </div>
        </TabsContent>
        <TabsContent value="favorites" className="mt-6">
          <div className="grid gap-4">
            {favoriteRecordings.map((recording) => (
              <RecordingItem key={recording.id} recording={recording} />
            ))}
          </div>
        </TabsContent>
        <TabsContent value="shared" className="mt-6">
          <div className="grid gap-4">
            {sharedRecordings.map((recording) => (
              <RecordingItem key={recording.id} recording={recording} />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

interface Recording {
  id: string
  title: string
  date: string
  duration: string
  hasTranscript: boolean
  hasAnalysis: boolean
}

function RecordingItem({ recording }: { recording: Recording }) {
  return (
    <Card className="overflow-hidden">
      <div className="flex items-center p-4">
        <div className="flex-1">
          <h3 className="font-medium">{recording.title}</h3>
          <div className="flex items-center text-sm text-muted-foreground mt-1">
            <Calendar className="h-3.5 w-3.5 mr-1" />
            <span>{recording.date}</span>
            <span className="mx-2">•</span>
            <Clock className="h-3.5 w-3.5 mr-1" />
            <span>{recording.duration}</span>
          </div>
        </div>
        <div className="flex gap-2">
          {recording.hasTranscript && (
            <Button variant="outline" size="sm">
              <FileText className="h-4 w-4 mr-1" />
              Transcript
            </Button>
          )}
          {recording.hasAnalysis && (
            <Button variant="outline" size="sm">
              <BarChart className="h-4 w-4 mr-1" />
              Analysis
            </Button>
          )}
          <Button size="sm">Open</Button>
        </div>
      </div>
    </Card>
  )
}

const recentRecordings: Recording[] = [
  {
    id: "1",
    title: "Weekly Team Meeting",
    date: "Today, 10:30 AM",
    duration: "45:12",
    hasTranscript: true,
    hasAnalysis: true,
  },
  {
    id: "2",
    title: "Client Interview - Project Alpha",
    date: "Yesterday, 2:15 PM",
    duration: "32:47",
    hasTranscript: true,
    hasAnalysis: false,
  },
  {
    id: "3",
    title: "Product Planning Session",
    date: "Mar 8, 2025",
    duration: "1:12:33",
    hasTranscript: true,
    hasAnalysis: true,
  },
  {
    id: "4",
    title: "Marketing Strategy Discussion",
    date: "Mar 5, 2025",
    duration: "28:05",
    hasTranscript: false,
    hasAnalysis: false,
  },
]

const favoriteRecordings: Recording[] = [
  {
    id: "5",
    title: "Quarterly Planning - Q1 2025",
    date: "Feb 28, 2025",
    duration: "1:45:22",
    hasTranscript: true,
    hasAnalysis: true,
  },
  {
    id: "6",
    title: "User Research Interviews",
    date: "Feb 15, 2025",
    duration: "52:18",
    hasTranscript: true,
    hasAnalysis: true,
  },
]

const sharedRecordings: Recording[] = [
  {
    id: "7",
    title: "Design Review with Sarah",
    date: "Mar 7, 2025",
    duration: "38:42",
    hasTranscript: true,
    hasAnalysis: false,
  },
  {
    id: "8",
    title: "Engineering Standup",
    date: "Mar 6, 2025",
    duration: "15:03",
    hasTranscript: true,
    hasAnalysis: true,
  },
]

