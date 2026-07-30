<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useCartStore } from '../../stores/cart'

const router = useRouter()
const route = useRoute()
const cart = useCartStore()
const { totalCount } = storeToRefs(cart)

const searchText = ref(route.query.q ? String(route.query.q) : '')

// Keep the input in sync when the route query changes (e.g. after navigation).
watch(
  () => route.query.q,
  (q) => {
    searchText.value = q ? String(q) : ''
  }
)

function doSearch() {
  const q = searchText.value.trim()
  if (!q) return
  router.push({ path: '/', query: { q } })
}

function goHome() {
  router.push('/')
}
</script>

<template>
  <header class="sticky top-0 z-40 glass border-b border-black/5">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-3 sm:gap-6">
      <!-- Logo -->
      <button
        @click="goHome"
        class="text-apple-blue font-semibold text-lg tracking-tight whitespace-nowrap flex items-center gap-1.5"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
          <path
            d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"
            stroke-linejoin="round"
          />
        </svg>
        <span class="hidden sm:inline">AI Mall</span>
      </button>

      <!-- Search -->
      <div class="flex-1 max-w-xl mx-auto relative">
        <svg
          class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          stroke-width="2"
        >
          <circle cx="11" cy="11" r="7" />
          <path d="m21 21-4.3-4.3" stroke-linecap="round" />
        </svg>
        <input
          v-model="searchText"
          @keyup.enter="doSearch"
          type="text"
          placeholder="AI 智能搜索商品..."
          class="w-full h-9 pl-9 pr-4 rounded-btn bg-black/5 text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:bg-white focus:ring-2 focus:ring-apple-blue/30 transition"
        />
      </div>

      <!-- Cart -->
      <router-link
        to="/cart"
        class="relative p-2 rounded-btn hover:bg-black/5 transition flex items-center"
        aria-label="购物车"
      >
        <svg
          class="w-5 h-5 text-text-primary"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          stroke-width="1.8"
        >
          <circle cx="9" cy="20" r="1.5" />
          <circle cx="18" cy="20" r="1.5" />
          <path
            d="M2.5 3h2.2l2.2 12.4a1.6 1.6 0 0 0 1.6 1.3h9.8a1.6 1.6 0 0 0 1.6-1.3L22 7H6"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        <span
          v-if="totalCount > 0"
          class="absolute -top-0 -right-0 bg-apple-blue text-white text-[10px] min-w-[16px] h-4 px-1 rounded-full flex items-center justify-center font-medium"
        >
          {{ totalCount > 99 ? '99+' : totalCount }}
        </span>
      </router-link>
    </div>
  </header>
</template>
