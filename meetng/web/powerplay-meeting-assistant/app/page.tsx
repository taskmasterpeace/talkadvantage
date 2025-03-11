import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import RecordingTab from "@/components/recording-tab"
import LibraryTab from "@/components/library-tab"
import DeepAnalysisTab from "@/components/deep-analysis-tab"
import ImportTab from "@/components/import-tab"
import { MicIcon, BookIcon, SearchIcon, UploadIcon } from "lucide-react"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <header className="border-b border-border p-4">
        <div className="container flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">
            PowerPlay <span className="text-muted-foreground text-lg font-normal">AI-Enhanced Meeting Assistant</span>
          </h1>
          <div className="flex items-center gap-4">
            <button className="text-muted-foreground hover:text-primary">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-settings"
              >
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
            </button>
            <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
              <span className="text-sm font-medium">JP</span>
            </div>
          </div>
        </div>
      </header>

      <div className="container py-6">
        <Tabs defaultValue="recording" className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-6">
            <TabsTrigger value="recording" className="flex items-center gap-2">
              <MicIcon className="h-4 w-4" />
              <span>Recording</span>
            </TabsTrigger>
            <TabsTrigger value="library" className="flex items-center gap-2">
              <BookIcon className="h-4 w-4" />
              <span>Library</span>
            </TabsTrigger>
            <TabsTrigger value="deep-analysis" className="flex items-center gap-2">
              <SearchIcon className="h-4 w-4" />
              <span>Deep Analysis</span>
            </TabsTrigger>
            <TabsTrigger value="import" className="flex items-center gap-2">
              <UploadIcon className="h-4 w-4" />
              <span>Import</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="recording">
            <RecordingTab />
          </TabsContent>

          <TabsContent value="library">
            <LibraryTab />
          </TabsContent>

          <TabsContent value="deep-analysis">
            <DeepAnalysisTab />
          </TabsContent>

          <TabsContent value="import">
            <ImportTab />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}

