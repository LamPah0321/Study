<script setup>
import { useChatOpen } from '../../composables/useChat'

const { open } = useChatOpen()
</script>

<template>
  <button
    @click="open()"
    class="fixed bottom-6 right-6 z-50 w-16 h-16 rounded-full glass border border-white/40 shadow-lg flex items-center justify-center transition-transform duration-300 hover:scale-110 active:scale-95 group"
    aria-label="AI 导购助手"
  >
    <!-- soft glow -->
    <span
      class="absolute inset-0 rounded-full bg-apple-blue/20 blur-md -z-10 group-hover:bg-apple-blue/30 transition"
    ></span>
    <svg
      class="w-7 h-7 text-apple-blue"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      stroke-width="2"
    >
      <path
        d="M12 2.5l1.9 5.6 5.6 1.9-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.9L12 2.5z"
        stroke-linejoin="round"
      />
      <path
        d="M18.5 14.5l.9 2.6 2.6.9-2.6.9-.9 2.6-.9-2.6-2.6-.9 2.6-.9.9-2.6z"
        stroke-linejoin="round"
      />
    </svg>
  </button>
</template>
