import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { ArrowRight, Mic, Calendar, FileText, BrainCircuit } from "lucide-react"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl">
            <BrainCircuit className="h-6 w-6 text-primary" />
            <span>MeetScribe</span>
          </div>
          <nav className="hidden md:flex gap-6">
            <Link href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
              Features
            </Link>
            <Link href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
            <Link href="#faq" className="text-muted-foreground hover:text-foreground transition-colors">
              FAQ
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="outline">Log in</Button>
            </Link>
            <Link href="/signup">
              <Button>Sign up</Button>
            </Link>
          </div>
        </div>
      </header>
      <main className="flex-1">
        <section className="py-20 md:py-32 bg-gradient-to-b from-background to-muted">
          <div className="container flex flex-col items-center text-center">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">AI-Enhanced Meeting Assistant</h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mb-10">
              Record, transcribe, analyze, and extract insights from your conversations, meetings, and interviews with
              advanced AI.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/signup">
                <Button size="lg" className="gap-2">
                  Get Started <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/demo">
                <Button size="lg" variant="outline">
                  Watch Demo
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section id="features" className="py-20 container">
          <h2 className="text-3xl font-bold text-center mb-16">Powerful Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <Mic className="h-10 w-10 text-primary mb-4" />
                <CardTitle>Recording & Transcription</CardTitle>
                <CardDescription>Capture high-quality audio and get real-time transcription</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2">
                  <li>Real-time audio recording</li>
                  <li>Live transcription as you speak</li>
                  <li>Bookmarking system</li>
                  <li>Voice commands</li>
                  <li>Flexible processing options</li>
                </ul>
              </CardContent>
              <CardFooter>
                <Link href="/features/recording">
                  <Button variant="outline" className="w-full">
                    Learn More
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            <Card>
              <CardHeader>
                <Calendar className="h-10 w-10 text-primary mb-4" />
                <CardTitle>Library Management</CardTitle>
                <CardDescription>Organize and access your recordings efficiently</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2">
                  <li>Calendar organization</li>
                  <li>Advanced search capabilities</li>
                  <li>Batch selection and processing</li>
                  <li>Media playback with waveform</li>
                  <li>Quick actions for common tasks</li>
                </ul>
              </CardContent>
              <CardFooter>
                <Link href="/features/library">
                  <Button variant="outline" className="w-full">
                    Learn More
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            <Card>
              <CardHeader>
                <FileText className="h-10 w-10 text-primary mb-4" />
                <CardTitle>AI-Powered Analysis</CardTitle>
                <CardDescription>Extract insights and improve your conversations</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2">
                  <li>Conversation Compass visualization</li>
                  <li>Curiosity Engine for questions</li>
                  <li>Multi-transcript analysis</li>
                  <li>Comparative visualizations</li>
                  <li>Contextual AI chat</li>
                </ul>
              </CardContent>
              <CardFooter>
                <Link href="/features/analysis">
                  <Button variant="outline" className="w-full">
                    Learn More
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          </div>
        </section>

        <section id="pricing" className="py-20 bg-muted">
          <div className="container">
            <h2 className="text-3xl font-bold text-center mb-16">Simple, Transparent Pricing</h2>
            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <Card>
                <CardHeader>
                  <CardTitle>Basic</CardTitle>
                  <div className="text-4xl font-bold">
                    $9<span className="text-lg font-normal text-muted-foreground">/month</span>
                  </div>
                  <CardDescription>For individual users</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5 space-y-2">
                    <li>5 hours of recording per month</li>
                    <li>Basic transcription</li>
                    <li>7-day recording history</li>
                    <li>Standard AI analysis</li>
                    <li>Email support</li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link href="/signup?plan=basic">
                    <Button className="w-full">Get Started</Button>
                  </Link>
                </CardFooter>
              </Card>

              <Card className="border-primary">
                <CardHeader>
                  <div className="py-1 px-3 rounded-full text-xs font-medium bg-primary text-primary-foreground w-fit mb-2">
                    POPULAR
                  </div>
                  <CardTitle>Professional</CardTitle>
                  <div className="text-4xl font-bold">
                    $29<span className="text-lg font-normal text-muted-foreground">/month</span>
                  </div>
                  <CardDescription>For professionals and small teams</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5 space-y-2">
                    <li>20 hours of recording per month</li>
                    <li>Advanced transcription with speaker detection</li>
                    <li>30-day recording history</li>
                    <li>Full AI analysis suite</li>
                    <li>Priority support</li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link href="/signup?plan=professional">
                    <Button className="w-full">Get Started</Button>
                  </Link>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Enterprise</CardTitle>
                  <div className="text-4xl font-bold">
                    $99<span className="text-lg font-normal text-muted-foreground">/month</span>
                  </div>
                  <CardDescription>For larger teams and organizations</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5 space-y-2">
                    <li>Unlimited recording hours</li>
                    <li>Premium transcription with custom vocabulary</li>
                    <li>Unlimited history</li>
                    <li>Custom AI models and analysis</li>
                    <li>Dedicated support manager</li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Link href="/contact-sales">
                    <Button className="w-full">Contact Sales</Button>
                  </Link>
                </CardFooter>
              </Card>
            </div>
          </div>
        </section>

        <section id="faq" className="py-20 container">
          <h2 className="text-3xl font-bold text-center mb-16">Frequently Asked Questions</h2>
          <div className="max-w-3xl mx-auto space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">How accurate is the transcription?</CardTitle>
              </CardHeader>
              <CardContent>
                <p>
                  Our transcription service achieves over 95% accuracy for clear audio in standard English. Accuracy may
                  vary based on audio quality, accents, and background noise. Professional and Enterprise plans include
                  enhanced accuracy with custom vocabulary options.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Is my data secure?</CardTitle>
              </CardHeader>
              <CardContent>
                <p>
                  Yes, we take data security seriously. All recordings and transcripts are encrypted both in transit and
                  at rest. We comply with GDPR, CCPA, and other privacy regulations. Enterprise plans include additional
                  security features like SSO and custom data retention policies.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Can I export my transcripts and analysis?</CardTitle>
              </CardHeader>
              <CardContent>
                <p>
                  You can export transcripts in multiple formats including TXT, DOCX, PDF, and SRT. Analysis results can
                  be exported as PDF reports or CSV data. Enterprise plans include API access for custom integrations
                  with your existing workflows.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-xl">What languages are supported?</CardTitle>
              </CardHeader>
              <CardContent>
                <p>
                  Our Basic plan supports English transcription. Professional plans add support for Spanish, French,
                  German, and Japanese. Enterprise plans include support for 50+ languages and dialects. Custom language
                  models are available for specialized terminology.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>
      <footer className="border-t py-10 bg-muted/50">
        <div className="container flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center gap-2 font-bold mb-4 md:mb-0">
            <BrainCircuit className="h-5 w-5 text-primary" />
            <span>MeetScribe</span>
          </div>
          <div className="flex flex-col md:flex-row gap-4 md:gap-8 text-sm text-muted-foreground text-center md:text-left">
            <Link href="/privacy" className="hover:text-foreground transition-colors">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-foreground transition-colors">
              Terms of Service
            </Link>
            <Link href="/contact" className="hover:text-foreground transition-colors">
              Contact Us
            </Link>
            <div>© {new Date().getFullYear()} MeetScribe. All rights reserved.</div>
          </div>
        </div>
      </footer>
    </div>
  )
}

