'use client'

import { useState } from 'react'

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<string>('')
  const [sceneThreshold, setSceneThreshold] = useState(0.4)
  const [maxScenes, setMaxScenes] = useState(10)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const analyzeVideo = async () => {
    if (!file) return
    
    setAnalyzing(true)
    const formData = new FormData()
    formData.append('video', file)
    formData.append('scene_threshold', sceneThreshold.toString())
    formData.append('max_scenes', maxScenes.toString())

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      })
      
      if (response.ok) {
        const data = await response.text()
        setResult(data || 'Analysis complete')
      } else {
        setResult('Error analyzing video')
      }
    } catch (error) {
      setResult('Error connecting to backend')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🎬 ClipWeaver</h1>
      <p>AI Storyboarder for AI Videos</p>
      
      <div style={{ margin: '2rem 0' }}>
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          style={{ marginBottom: '1rem', display: 'block' }}
        />
        
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>
            Scene Detection Sensitivity: {sceneThreshold}
            <br />
            <small style={{ color: '#666' }}>Lower = more scenes detected (0.1 = very sensitive, 0.9 = less sensitive)</small>
          </label>
          <input
            type="range"
            min="0.1"
            max="0.9"
            step="0.1"
            value={sceneThreshold}
            onChange={(e) => setSceneThreshold(parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>
            Maximum Scenes: {maxScenes}
          </label>
          <input
            type="range"
            min="1"
            max="20"
            step="1"
            value={maxScenes}
            onChange={(e) => setMaxScenes(parseInt(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>
        
        <button
          onClick={analyzeVideo}
          disabled={!file || analyzing}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: analyzing ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: analyzing ? 'not-allowed' : 'pointer'
          }}
        >
          {analyzing ? 'Analyzing...' : 'Analyze Video'}
        </button>
      </div>

      {result && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Result:</h3>
          <pre style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '1rem', 
            borderRadius: '4px',
            whiteSpace: 'pre-wrap'
          }}>
            {result}
          </pre>
        </div>
      )}
    </main>
  )
}
