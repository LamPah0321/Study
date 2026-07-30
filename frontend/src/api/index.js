import axios from 'axios'

const BASE_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ---- Simple non-blocking toast (no external deps) ----
function showToast(message) {
  let el = document.getElementById('app-toast')
  if (!el) {
    el = document.createElement('div')
    el.id = 'app-toast'
    el.style.cssText =
      'position:fixed;top:24px;left:50%;transform:translateX(-50%);' +
      'background:rgba(0,0,0,0.82);color:#fff;padding:12px 20px;border-radius:8px;' +
      'z-index:9999;font-size:14px;max-width:80%;text-align:center;line-height:1.4;' +
      'box-shadow:0 4px 20px rgba(0,0,0,0.2);opacity:0;transition:opacity .2s ease;' +
      'font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Helvetica Neue",sans-serif;'
    document.body.appendChild(el)
  }
  el.textContent = message
  el.style.display = 'block'
  // force reflow then fade in
  void el.offsetWidth
  el.style.opacity = '1'
  clearTimeout(el._timer)
  el._timer = setTimeout(() => {
    el.style.opacity = '0'
    setTimeout(() => {
      el.style.display = 'none'
    }, 220)
  }, 3000)
}

// ---- Interceptors ----
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = '请求失败'
    if (error.response) {
      message = error.response.data?.detail || error.response.data?.message || `请求失败 (${error.response.status})`
    } else if (error.request) {
      message = '网络异常，请检查连接'
    } else {
      message = error.message || '请求失败'
    }
    showToast(message)
    return Promise.reject(error)
  }
)

// ---- Product APIs ----
export function getProducts(params) {
  return api.get('/products', { params }).then((r) => r.data)
}

export function getProduct(id) {
  return api.get(`/products/${id}`).then((r) => r.data)
}

export function createProduct(data) {
  return api.post('/products', data).then((r) => r.data)
}

export function updateProduct(id, data) {
  return api.put(`/products/${id}`, data).then((r) => r.data)
}

export function deleteProduct(id) {
  return api.delete(`/products/${id}`).then((r) => r.data)
}

// ---- Semantic search ----
export function semanticSearch(query, top_k = 5) {
  return api.post('/search/semantic', { query, top_k }).then((r) => r.data)
}

// ---- Cart checkout ----
export function checkoutCart(items) {
  return api.post('/cart/checkout', { items }).then((r) => r.data)
}

// ---- Streaming chat (SSE) ----
// Uses fetch directly (NOT axios) to stream the response body.
// Returns a controller object with an `abort()` method and a `done` promise.
export function streamChat(message, history, onChunk) {
  const controller = new AbortController()

  const done = (async () => {
    const res = await fetch(`${BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
      signal: controller.signal,
    })

    if (!res.ok) {
      let detail = `HTTP ${res.status}`
      try {
        const data = await res.json()
        detail = data.detail || data.message || detail
      } catch (e) {
        /* ignore */
      }
      throw new Error(detail)
    }

    if (!res.body) {
      throw new Error('当前环境不支持流式响应')
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    const handleData = (data) => {
      if (!data || data === '[DONE]') return false
      try {
        const parsed = JSON.parse(data)
        const content =
          parsed.content ?? parsed.delta ?? parsed.message ?? parsed.text ?? ''
        if (content) onChunk(content)
      } catch (e) {
        // Not JSON — treat as plain text content.
        onChunk(data)
      }
      return true
    }

    const processBuffer = (final = false) => {
      const lines = buffer.split('\n')
      // keep the last (possibly incomplete) line in the buffer unless final
      buffer = final ? '' : lines.pop()
      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data:')) continue
        const data = trimmed.slice(5).trim()
        if (!handleData(data)) return false // [DONE]
      }
      return true
    }

    while (true) {
      const { done: readerDone, value } = await reader.read()
      if (readerDone) break
      buffer += decoder.decode(value, { stream: true })
      if (!processBuffer(false)) break
    }
    // flush any trailing data
    processBuffer(true)
  })()

  return {
    abort: () => controller.abort(),
    done,
  }
}
