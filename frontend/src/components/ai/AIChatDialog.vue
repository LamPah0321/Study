<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useChatOpen } from '../../composables/useChat'
import { streamChat } from '../../api'

const { isOpen, close, pendingQuestion } = useChatOpen()

const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是 AI 导购助手，可以帮你推荐和查找商品，请问有什么可以帮你的？',
  },
])
const input = ref('')
const streaming = ref(false)
const bodyRef = ref(null)
let controller = null

function scrollToBottom() {
  nextTick(() => {
    if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight
  })
}

// Prefill input when a product page asks the AI a question.
watch(
  pendingQuestion,
  (q) => {
    if (q) input.value = q
  }
)

async function send() {
  const text = input.value.trim()
  if (!text || streaming.value) return

  input.value = ''
  messages.value.push({ role: 'user', content: text })
  messages.value.push({ role: 'assistant', content: '' })
  const aiIndex = messages.value.length - 1
  streaming.value = true
  scrollToBottom()

  // Build history from everything before the current user message.
  const history = messages.value
    .slice(0, aiIndex - 1)
    .map((m) => ({ role: m.role, content: m.content }))

  controller = streamChat(text, history, (chunk) => {
    messages.value[aiIndex].content += chunk
    scrollToBottom()
  })

  try {
    await controller.done
  } catch (e) {
    if (e && e.name === 'AbortError') {
      // user cancelled — keep the partial content as-is
      if (!messages.value[aiIndex].content) {
        messages.value[aiIndex].content = '（已停止）'
      }
    } else {
      messages.value[aiIndex].content +=
        (messages.value[aiIndex].content ? '\n\n' : '') +
        '[请求出错，请稍后重试]'
    }
  } finally {
    streaming.value = false
    controller = null
    scrollToBottom()
  }
}

function stop() {
  if (controller) {
    controller.abort()
  }
}

function handleEnter(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

// Clean up any in-flight stream if the dialog closes.
watch(isOpen, (open) => {
  if (!open && controller) {
    controller.abort()
  }
})

onBeforeUnmount(() => {
  if (controller) controller.abort()
})
</script>

<template>
  <transition name="chat">
    <div
      v-if="isOpen"
      class="fixed bottom-24 right-4 sm:right-6 z-50 w-[92vw] max-w-sm"
    >
      <div
        class="rounded-card overflow-hidden shadow-2xl glass border border-white/40 flex flex-col"
        style="height: 70vh; max-height: 560px"
      >
        <!-- Header -->
        <div
          class="glass border-b border-black/5 px-4 py-3 flex items-center justify-between flex-shrink-0"
        >
          <div class="flex items-center gap-2">
            <svg
              class="w-5 h-5 text-apple-blue"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              stroke-width="2"
            >
              <path
                d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"
                stroke-linejoin="round"
              />
            </svg>
            <span class="font-semibold text-text-primary">AI 导购助手</span>
          </div>
          <button
            @click="close"
            class="p-1.5 rounded-btn hover:bg-black/10 transition"
            aria-label="关闭"
          >
            <svg
              class="w-4 h-4 text-text-primary"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              stroke-width="2"
            >
              <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <!-- Messages -->
        <div
          ref="bodyRef"
          class="flex-1 overflow-y-auto px-4 py-3 space-y-3"
        >
          <div
            v-for="(m, i) in messages"
            :key="i"
            :class="[
              'flex',
              m.role === 'user' ? 'justify-end' : 'justify-start',
            ]"
          >
            <div
              :class="[
                'max-w-[80%] px-3.5 py-2 text-sm leading-relaxed whitespace-pre-wrap break-words',
                m.role === 'user'
                  ? 'bg-apple-blue text-white rounded-2xl rounded-br-md'
                  : 'bg-white/80 text-text-primary rounded-2xl rounded-bl-md border border-black/5',
              ]"
            >
              <template v-if="m.content">{{ m.content }}</template>
              <span
                v-else-if="streaming && i === messages.length - 1"
                class="flex items-center gap-1 py-1"
              >
                <span
                  class="w-1.5 h-1.5 bg-text-secondary rounded-full animate-bounce"
                  style="animation-delay: 0ms"
                ></span>
                <span
                  class="w-1.5 h-1.5 bg-text-secondary rounded-full animate-bounce"
                  style="animation-delay: 150ms"
                ></span>
                <span
                  class="w-1.5 h-1.5 bg-text-secondary rounded-full animate-bounce"
                  style="animation-delay: 300ms"
                ></span>
              </span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="border-t border-black/5 p-3 glass flex-shrink-0">
          <div class="flex items-center gap-2">
            <input
              v-model="input"
              @keydown="handleEnter"
              :disabled="streaming"
              type="text"
              placeholder="输入你的问题..."
              class="flex-1 h-10 px-3 rounded-btn bg-black/5 text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:bg-white focus:ring-2 focus:ring-apple-blue/30 transition disabled:opacity-60"
            />
            <button
              v-if="!streaming"
              @click="send"
              class="h-10 px-4 rounded-btn bg-apple-blue text-white text-sm font-medium hover:opacity-90 transition active:scale-95 flex-shrink-0"
            >
              发送
            </button>
            <button
              v-else
              @click="stop"
              class="h-10 px-4 rounded-btn bg-black/10 text-text-primary text-sm font-medium hover:bg-black/20 transition flex-shrink-0"
            >
              停止
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.chat-enter-active,
.chat-leave-active {
  transition: all 0.25s ease;
}
.chat-enter-from,
.chat-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.96);
}
</style>
