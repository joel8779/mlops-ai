"use client";

import { motion } from "framer-motion";
import { 
  Brain, 
  Search, 
  FileText, 
  MessageSquare, 
  Scan, 
  BarChart3,
  ArrowRight,
  Check,
  Zap,
  Shield,
  Globe,
  Users,
  TrendingUp,
  Sparkles
} from "lucide-react";
import Link from "next/link";
import { fadeInUp, fadeInLeft, fadeInRight, scaleIn } from "@/lib/animations";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 py-32 lg:px-8">
        <div className="relative mx-auto max-w-5xl">
          <motion.div
            {...fadeInUp}
            className="text-center"
          >
            <div className="mb-8 inline-flex items-center gap-2 rounded-full bg-background-card border border-background-border px-4 py-2">
              <Sparkles className="h-4 w-4 text-accent" />
              <span className="text-sm text-foreground-muted">AI-Native Hiring Infrastructure</span>
            </div>
            
            <h1 className="mb-6 text-5xl font-bold tracking-tight lg:text-7xl">
              Hire Smarter with AI
            </h1>
            
            <p className="mx-auto mb-10 max-w-2xl text-lg text-foreground-muted">
              Transform your recruiting workflow with semantic search, AI-powered candidate ranking, 
              and intelligent document analysis. Built for modern recruiting teams.
            </p>
            
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Link
                href="/sign-up"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-8 py-4 text-lg font-semibold hover:bg-accent/90 transition-colors"
              >
                Get Started Free
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                href="#features"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-background-card border border-background-border px-8 py-4 text-lg font-semibold hover:bg-background-elevated transition-colors"
              >
                See How It Works
              </Link>
            </div>
          </motion.div>

          {/* Dashboard Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="mt-20 rounded-xl bg-background-card border border-background-border p-2 shadow-subtle"
          >
            <div className="rounded-lg bg-background-elevated p-6">
              <div className="flex gap-4 mb-6">
                <div className="h-3 w-3 rounded-full bg-foreground-disabled" />
                <div className="h-3 w-3 rounded-full bg-foreground-disabled" />
                <div className="h-3 w-3 rounded-full bg-foreground-disabled" />
              </div>
              <div className="grid gap-4 md:grid-cols-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="rounded-lg bg-background-card p-4 border border-background-border">
                    <div className="h-2 w-20 bg-background-border rounded mb-3" />
                    <div className="h-8 w-16 bg-accent/10 rounded" />
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* AI Recruiting Showcase */}
      <section id="features" className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <motion.div
            {...fadeInUp}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">AI-Powered Recruiting</h2>
            <p className="text-lg text-foreground-muted max-w-2xl mx-auto">
              Leverage cutting-edge AI to find, rank, and engage the best candidates faster than ever
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                icon: Brain,
                title: "AI Candidate Ranking",
                description: "Automatically rank candidates based on skills, experience, and job fit using advanced ML models"
              },
              {
                icon: Zap,
                title: "Instant Insights",
                description: "Get AI-generated candidate summaries, skill gaps, and interview recommendations in seconds"
              },
              {
                icon: Shield,
                title: "Bias Reduction",
                description: "AI-powered analysis helps reduce unconscious bias by focusing on skills and qualifications"
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                {...fadeInUp}
                transition={{ delay: i * 0.1 }}
                className="group rounded-xl bg-background-card border border-background-border p-8 hover:border-accent/50 transition-colors"
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
                  <feature.icon className="h-6 w-6 text-accent" />
                </div>
                <h3 className="mb-2 text-xl font-semibold">{feature.title}</h3>
                <p className="text-foreground-muted">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Semantic Search Showcase */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-16 lg:grid-cols-2 items-center">
            <motion.div
              {...fadeInLeft}
            >
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-2 border border-accent/20">
                <Search className="h-4 w-4 text-accent" />
                <span className="text-sm text-accent">Semantic Search</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">Find Candidates by Meaning, Not Keywords</h2>
              <p className="text-lg text-foreground-muted mb-6">
                Search for "Python backend engineers with Docker experience" and find candidates who match the intent, 
                even if they use different terminology. Our semantic understanding goes beyond simple keyword matching.
              </p>
              <ul className="space-y-3">
                {[
                  "Natural language search queries",
                  "Skill-based matching",
                  "Experience-level filtering",
                  "Real-time result ranking"
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-foreground">
                    <Check className="h-5 w-5 text-accent flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
            
            <motion.div
              {...fadeInRight}
              className="rounded-xl bg-background-card border border-background-border p-8"
            >
              <div className="space-y-4">
                <div className="rounded-lg bg-background-elevated p-4 border border-background-border">
                  <div className="text-sm text-foreground-muted mb-2">Search Query</div>
                  <div className="text-foreground">"Senior Python developer with ML experience"</div>
                </div>
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="rounded-lg bg-background-elevated p-4 border border-background-border flex items-center gap-4">
                      <div className="h-10 w-10 rounded-full bg-accent/20" />
                      <div className="flex-1">
                        <div className="text-foreground font-medium">Candidate {i}</div>
                        <div className="text-sm text-foreground-muted">98% match • ML Engineer</div>
                      </div>
                      <div className="text-accent font-semibold">98%</div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ATS Scoring Showcase */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-16 lg:grid-cols-2 items-center">
            <motion.div
              {...fadeInRight}
              className="order-2 lg:order-1"
            >
              <div className="rounded-xl bg-background-card border border-background-border p-8">
                <div className="grid gap-6">
                  {[
                    { name: "Technical Skills", score: 92 },
                    { name: "Experience", score: 88 },
                    { name: "Education", score: 95 },
                    { name: "Cultural Fit", score: 85 }
                  ].map((item, i) => (
                    <div key={i} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-foreground">{item.name}</span>
                        <span className="text-accent">{item.score}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-background-border overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${item.score}%` }}
                          transition={{ duration: 0.8, delay: i * 0.1, ease: "easeOut" }}
                          className="h-full bg-accent"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
            
            <motion.div
              {...fadeInLeft}
              className="order-1 lg:order-2"
            >
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-2 border border-accent/20">
                <FileText className="h-4 w-4 text-accent" />
                <span className="text-sm text-accent">ATS Scoring</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">Intelligent Resume Analysis</h2>
              <p className="text-lg text-foreground-muted mb-6">
                Our AI-powered ATS scoring analyzes resumes across multiple dimensions - technical skills, 
                experience, education, and cultural fit - to provide comprehensive candidate evaluations.
              </p>
              <ul className="space-y-3">
                {[
                  "Multi-dimensional scoring",
                  "Skill extraction and validation",
                  "Experience gap analysis",
                  "Automated screening"
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-foreground">
                    <Check className="h-5 w-5 text-accent flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* AI Copilot Showcase */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-16 lg:grid-cols-2 items-center">
            <motion.div
              {...fadeInLeft}
            >
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-2 border border-accent/20">
                <MessageSquare className="h-4 w-4 text-accent" />
                <span className="text-sm text-accent">AI Copilot</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">Your AI Recruiting Assistant</h2>
              <p className="text-lg text-foreground-muted mb-6">
                Get instant help with candidate questions, interview preparation, and hiring decisions. 
                Our AI copilot understands your context and provides actionable recommendations.
              </p>
              <ul className="space-y-3">
                {[
                  "Candidate Q&A assistance",
                  "Interview question generation",
                  "Offer recommendation insights",
                  "24/7 availability"
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-foreground">
                    <Check className="h-5 w-5 text-accent flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
            
            <motion.div
              {...fadeInRight}
              className="rounded-xl bg-background-card border border-background-border p-8"
            >
              <div className="space-y-4">
                <div className="rounded-lg bg-background-elevated p-4 border border-background-border">
                  <div className="text-sm text-foreground-muted mb-2">You</div>
                  <div className="text-foreground">What questions should I ask about their ML experience?</div>
                </div>
                <div className="rounded-lg bg-accent/10 p-4 border border-accent/20">
                  <div className="text-sm text-accent mb-2">AI Copilot</div>
                  <div className="text-foreground">
                    Here are some key questions: 1) What ML frameworks have you used? 2) Can you describe a project where you deployed a model to production? 3) How do you handle model drift?
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* OCR/Document Intelligence Showcase */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-16 lg:grid-cols-2 items-center">
            <motion.div
              {...fadeInRight}
              className="order-2 lg:order-1"
            >
              <div className="rounded-xl bg-background-card border border-background-border p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="h-16 w-16 rounded-lg bg-accent/20 flex items-center justify-center">
                    <Scan className="h-8 w-8 text-accent" />
                  </div>
                  <div>
                    <div className="text-foreground font-semibold">Resume Analysis</div>
                    <div className="text-sm text-foreground-muted">Processing complete</div>
                  </div>
                </div>
                <div className="space-y-3">
                  {[
                    "Skills extracted: 12",
                    "Experience parsed: 5 years",
                    "Education verified",
                    "Certifications detected: 3"
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-3 text-foreground">
                      <Check className="h-4 w-4 text-accent flex-shrink-0" />
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
            
            <motion.div
              {...fadeInLeft}
              className="order-1 lg:order-2"
            >
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-2 border border-accent/20">
                <Scan className="h-4 w-4 text-accent" />
                <span className="text-sm text-accent">Document Intelligence</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">Smart Document Processing</h2>
              <p className="text-lg text-foreground-muted mb-6">
                Upload any resume format - PDF, Word, or images. Our OCR and document intelligence 
                extracts structured data, skills, and experience automatically.
              </p>
              <ul className="space-y-3">
                {[
                  "Multi-format support",
                  "OCR for scanned documents",
                  "Structured data extraction",
                  "Bulk processing"
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-foreground">
                    <Check className="h-5 w-5 text-accent flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Analytics Showcase */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <motion.div
            {...fadeInUp}
            className="text-center mb-16"
          >
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-2 border border-accent/20">
              <BarChart3 className="h-4 w-4 text-accent" />
              <span className="text-sm text-accent">Analytics</span>
            </div>
            <h2 className="text-4xl font-bold mb-4">Data-Driven Hiring Decisions</h2>
            <p className="text-lg text-foreground-muted max-w-2xl mx-auto">
              Track your hiring pipeline, measure recruiter performance, and optimize your process with comprehensive analytics
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-4">
            {[
              { label: "Time to Hire", value: "14 days", change: "-23%", icon: TrendingUp },
              { label: "Quality of Hire", value: "4.2/5", change: "+15%", icon: Users },
              { label: "Interview Rate", value: "68%", change: "+12%", icon: BarChart3 },
              { label: "Offer Acceptance", value: "85%", change: "+8%", icon: Globe }
            ].map((metric, i) => (
              <motion.div
                key={i}
                {...fadeInUp}
                transition={{ delay: i * 0.1 }}
                className="rounded-xl bg-background-card border border-background-border p-6"
              >
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10">
                  <metric.icon className="h-5 w-5 text-accent" />
                </div>
                <div className="text-2xl font-bold mb-1">{metric.value}</div>
                <div className="text-sm text-foreground-muted mb-2">{metric.label}</div>
                <div className="text-sm text-success">{metric.change} vs last month</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <motion.div
            {...fadeInUp}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">Everything You Need</h2>
            <p className="text-lg text-foreground-muted max-w-2xl mx-auto">
              A complete recruiting platform built for modern teams
            </p>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              "Candidate Management",
              "Job Posting & Distribution",
              "Interview Scheduling",
              "Team Collaboration",
              "Email Templates",
              "Reporting & Exports",
              "API Access",
              "SSO & Security",
              "Mobile App"
            ].map((feature, i) => (
              <motion.div
                key={i}
                {...scaleIn}
                transition={{ delay: i * 0.05 }}
                className="rounded-lg bg-background-card border border-background-border p-4 text-center hover:bg-background-elevated transition-colors"
              >
                {feature}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <motion.div
            {...fadeInUp}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">Trusted by Leading Teams</h2>
            <p className="text-lg text-foreground-muted max-w-2xl mx-auto">
              See how companies are transforming their recruiting with AI
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                quote: "Resume AI reduced our time-to-hire by 40% and improved candidate quality significantly.",
                author: "Sarah Chen",
                role: "Head of Talent, TechCorp",
                company: "TechCorp"
              },
              {
                quote: "The semantic search is incredible. We find candidates we would have missed with keyword search.",
                author: "Michael Rodriguez",
                role: "Recruiting Manager, StartupXYZ",
                company: "StartupXYZ"
              },
              {
                quote: "AI Copilot feels like having an extra team member. It's transformed how we approach hiring.",
                author: "Emily Watson",
                role: "HR Director, GrowthCo",
                company: "GrowthCo"
              }
            ].map((testimonial, i) => (
              <motion.div
                key={i}
                {...fadeInUp}
                transition={{ delay: i * 0.1 }}
                className="rounded-xl bg-background-card border border-background-border p-8"
              >
                <div className="mb-6 text-lg text-foreground-muted">"{testimonial.quote}"</div>
                <div>
                  <div className="font-semibold text-foreground">{testimonial.author}</div>
                  <div className="text-sm text-foreground-muted">{testimonial.role}, {testimonial.company}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <motion.div
            {...scaleIn}
            className="relative overflow-hidden rounded-2xl bg-accent p-12 text-center"
          >
            <div className="relative">
              <h2 className="text-4xl font-bold mb-4 text-white">Ready to Transform Your Hiring?</h2>
              <p className="text-lg text-white/80 mb-8 max-w-2xl mx-auto">
                Join hundreds of recruiting teams using AI to hire smarter and faster
              </p>
              <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
                <Link
                  href="/sign-up"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-8 py-4 text-lg font-semibold text-accent hover:bg-white/90 transition-colors"
                >
                  Start Free Trial
                  <ArrowRight className="h-5 w-5" />
                </Link>
                <Link
                  href="#"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-white/10 px-8 py-4 text-lg font-semibold backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-colors text-white"
                >
                  Schedule Demo
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 lg:px-8 border-t border-background-border">
        <div className="mx-auto max-w-5xl">
          <div className="grid gap-8 md:grid-cols-4 mb-12">
            <div>
              <div className="text-xl font-bold mb-4">Resume AI</div>
              <p className="text-foreground-muted text-sm">
                AI-native hiring infrastructure for modern recruiting teams
              </p>
            </div>
            <div>
              <div className="font-semibold mb-4">Product</div>
              <ul className="space-y-2 text-sm text-foreground-muted">
                <li><Link href="#" className="hover:text-foreground transition-colors">Features</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">Pricing</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">Integrations</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">API</Link></li>
              </ul>
            </div>
            <div>
              <div className="font-semibold mb-4">Company</div>
              <ul className="space-y-2 text-sm text-foreground-muted">
                <li><Link href="#" className="hover:text-foreground transition-colors">About</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">Blog</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">Careers</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">Contact</Link></li>
              </ul>
            </div>
            <div>
              <div className="font-semibold mb-4">Legal</div>
              <ul className="space-y-2 text-sm text-foreground-muted">
                <li><Link href="#" className="hover:text-foreground transition-colors">Privacy</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">Terms</Link></li>
                <li><Link href="#" className="hover:text-foreground transition-colors">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-background-border pt-8 text-center text-sm text-foreground-muted">
            © 2025 Resume AI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
