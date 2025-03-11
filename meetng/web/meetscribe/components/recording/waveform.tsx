"use client"

import { useEffect, useRef } from "react"

interface WaveformProps {
  isActive: boolean
}

export function Waveform({ isActive }: WaveformProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || !isActive) return

    const container = containerRef.current
    const bars = Array.from(container.querySelectorAll(".waveform-bar"))

    let animationId: number

    const animate = () => {
      bars.forEach((bar, i) => {
        const height = Math.floor(Math.random() * 60) + 10
        ;(bar as HTMLElement).style.height = `${height}%`
      })

      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      cancelAnimationFrame(animationId)
      bars.forEach((bar) => {
        ;(bar as HTMLElement).style.height = "10%"
      })
    }
  }, [isActive])

  return (
    <div className="waveform-container" ref={containerRef}>
      <div className="waveform">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="waveform-bar"
            style={{
              height: isActive ? "10%" : "10%",
            }}
          />
        ))}
      </div>
    </div>
  )
}

