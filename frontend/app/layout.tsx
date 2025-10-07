import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ClipWeaver',
  description: 'AI Storyboarder for AI Videos',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
