<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getProducts } from '../api'
import ProductGrid from '../components/product/ProductGrid.vue'
import SearchResult from '../components/ai/SearchResult.vue'

const route = useRoute()

const products = ref([])
const loading = ref(false)
const activeCategory = ref('全部')

const searchQuery = computed(() =>
  route.query.q ? String(route.query.q) : ''
)

const categories = computed(() => {
  const set = new Set(['全部'])
  products.value.forEach((p) => {
    if (p.category) set.add(p.category)
  })
  return [...set]
})

const filtered = computed(() => {
  if (activeCategory.value === '全部') return products.value
  return products.value.filter((p) => p.category === activeCategory.value)
})

async function load() {
  loading.value = true
  try {
    const data = await getProducts()
    products.value = Array.isArray(data)
      ? data
      : data.items || data.products || data.results || []
  } catch (e) {
    // error already surfaced via axios interceptor
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div
        class="absolute inset-0 bg-gradient-to-b from-blue-50 via-bg-gray to-transparent"
      ></div>
      <div class="relative max-w-6xl mx-auto px-6 py-16 sm:py-20 text-center">
        <h1
          class="text-4xl sm:text-5xl font-bold text-text-primary tracking-tight"
        >
          AI 智能商城
        </h1>
        <p class="mt-4 text-lg text-text-secondary">
          用自然语言描述需求，让 AI 为你精选好物
        </p>
        <div
          class="mt-3 inline-flex items-center gap-1.5 text-sm text-apple-blue"
        >
          <svg
            class="w-4 h-4"
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
          <span>顶部搜索框即可体验 AI 语义搜索</span>
        </div>
      </div>
    </section>

    <div class="max-w-6xl mx-auto px-4 sm:px-6 pb-16">
      <!-- Search results take over the page when a query is present -->
      <SearchResult v-if="searchQuery" :query="searchQuery" :key="searchQuery" />

      <template v-else>
        <!-- Category chips -->
        <div class="flex flex-wrap gap-3 mb-8">
          <button
            v-for="c in categories"
            :key="c"
            @click="activeCategory = c"
            :class="[
              'px-4 py-2 rounded-full text-sm font-medium transition',
              activeCategory === c
                ? 'bg-apple-blue text-white shadow-card'
                : 'bg-white text-text-secondary hover:bg-black/5',
            ]"
          >
            {{ c }}
          </button>
        </div>

        <!-- Loading skeleton -->
        <div
          v-if="loading"
          class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
        >
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

        <ProductGrid v-else :products="filtered" />
      </template>
    </div>
  </div>
</template>
