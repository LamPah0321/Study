<script setup>
import { ref, watch } from 'vue'
import { semanticSearch } from '../../api'
import ProductGrid from '../product/ProductGrid.vue'

const props = defineProps({
  query: { type: String, required: true },
})

const loading = ref(false)
const error = ref('')
const summary = ref('')
const products = ref([])

async function runSearch(q) {
  if (!q) return
  loading.value = true
  error.value = ''
  summary.value = ''
  products.value = []
  try {
    const data = await semanticSearch(q, 5)
    summary.value = data.ai_summary || data.summary || ''
    products.value = data.products || data.results || data.items || []
  } catch (e) {
    error.value = e.response?.data?.detail || '搜索失败，请重试'
  } finally {
    loading.value = false
  }
}

watch(() => props.query, (q) => runSearch(q), { immediate: true })
</script>

<template>
  <div class="space-y-6">
    <!-- Query echo -->
    <div class="flex items-center gap-2 text-text-secondary text-sm">
      <svg
        class="w-4 h-4 text-apple-blue"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        stroke-width="2"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="m21 21-4.3-4.3" stroke-linecap="round" />
      </svg>
      <span>搜索关键词：<span class="text-text-primary font-medium">{{ query }}</span></span>
    </div>

    <!-- AI summary card -->
    <div
      class="glass border border-white/40 rounded-card p-6 shadow-card"
    >
      <div class="flex items-center gap-2 mb-3">
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
        <span class="font-semibold text-text-primary">AI 智能推荐</span>
      </div>
      <p class="text-text-primary leading-relaxed whitespace-pre-wrap">
        <span v-if="loading" class="text-text-secondary"
          >AI 正在为你分析「{{ query }}」...</span
        >
        <span v-else-if="summary">{{ summary }}</span>
        <span v-else class="text-text-secondary">暂无 AI 推荐内容</span>
      </p>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <div
        v-for="i in 8"
        :key="i"
        class="bg-white rounded-card shadow-card overflow-hidden"
      >
        <div class="aspect-square bg-black/5 animate-pulse"></div>
        <div class="p-5 space-y-2">
          <div class="h-4 bg-black/5 rounded animate-pulse"></div>
          <div class="h-4 w-1/2 bg-black/5 rounded animate-pulse"></div>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-16">
      <p class="text-text-secondary mb-2">{{ error }}</p>
      <p class="text-sm text-text-secondary">请尝试重新搜索</p>
    </div>

    <!-- Results -->
    <div v-else>
      <h3 class="text-lg font-semibold text-text-primary mb-4">相关商品</h3>
      <ProductGrid :products="products" />
    </div>
  </div>
</template>
