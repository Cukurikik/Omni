import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'OMNI TOOLS | Enterprise Hybrid Platform',
  description: 'Enterprise Hybrid Platform untuk pemrosesan Video, Audio, Image, PDF, AI dan LLM dengan performa highest-tier menggunakan C++, Golang, dan Python.',
  keywords: ['video converter', 'audio tools', 'image processing', 'pdf tools', 'AI', 'LLM', 'omni'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="id">
      <body className="antialiased">
        <div className="min-h-screen bg-[#0a0a0f]">
          {children}
        </div>
      </body>
    </html>
  )
}