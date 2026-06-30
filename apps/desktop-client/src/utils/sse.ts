import type { GenerationEvent, GenerationEventData } from '@/types'

export async function* streamSSE(response: Response): AsyncGenerator<GenerationEvent> {
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('Response body is null')
  }

  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        continue
      }

      if (line.startsWith('data: ')) {
        const dataStr = line.slice(6)
        if (dataStr === '[DONE]') {
          return
        }
        try {
          const data: GenerationEventData = JSON.parse(dataStr)
          yield { event: 'token', data }
        } catch {
          continue
        }
      }
    }
  }
}

export function parseSSEChunk(chunk: string): GenerationEvent | null {
  const lines = chunk.split('\n')
  let eventType: GenerationEvent['event'] = 'token'
  let data: GenerationEventData | null = null

  for (const line of lines) {
    if (line.startsWith('event: ')) {
      eventType = line.slice(7) as GenerationEvent['event']
    } else if (line.startsWith('data: ')) {
      const dataStr = line.slice(6)
      try {
        data = JSON.parse(dataStr)
      } catch {
        return null
      }
    }
  }

  if (!data) return null
  return { event: eventType, data }
}
