import { ref, onMounted, onUnmounted } from 'vue'
import { API_BASE_URL } from '@/lib/api'

// Global event bus to easily listen to WS events anywhere in the app
import mitt from 'mitt'
export const wsEvents = mitt()

let socket: WebSocket | null = null
let isConnected = false
let reconnectTimer: any = null

function connectWebSocket() {
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return
  }

  const token = localStorage.getItem('token')
  if (!token) return

  // Convert HTTP URL to WS URL
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  // Extract domain/port from API_BASE_URL, handling relative URLs or full URLs
  let wsUrl = ''
  if (API_BASE_URL.startsWith('http')) {
    const url = new URL(API_BASE_URL)
    wsUrl = `${wsProtocol}//${url.host}/api/ws?token=${token}`
  } else {
    wsUrl = `${wsProtocol}//${window.location.host}/api/ws?token=${token}`
  }

  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    console.log('WebSocket connected')
    isConnected = true
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('WebSocket message received:', data)
      wsEvents.emit(data.type, data.data)
    } catch (e) {
      console.error('Failed to parse WebSocket message', e)
    }
  }

  socket.onclose = () => {
    console.log('WebSocket disconnected')
    isConnected = false
    socket = null
    // Attempt to reconnect after 3 seconds
    if (!reconnectTimer && localStorage.getItem('token')) {
      reconnectTimer = setTimeout(() => {
        reconnectTimer = null
        connectWebSocket()
      }, 3000)
    }
  }

  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}

export function disconnectWebSocket() {
  if (socket) {
    socket.close()
    socket = null
  }
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
}

export function useWebSocket() {
  onMounted(() => {
    connectWebSocket()
  })

  onUnmounted(() => {
    // We don't automatically disconnect on unmount because 
    // the composable might be used across page navigations.
    // Call disconnectWebSocket manually on logout.
  })

  return {
    wsEvents
  }
}
