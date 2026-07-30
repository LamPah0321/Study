<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProduct } from '../api'
import { useCartStore } from '../stores/cart'
import { useChatOpen } from '../composables/useChat'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const { open } = useChatOpen()

const product = ref(null)
const loading = ref(true)
const added = ref(false)
const imgError = ref(false)

const price = computed(() => {
  if (!product.value) return '0.00'
  const p = Number(product.value.price)
  return isNaN(p) ? '0.00' : p.toFixed(2)
})

// Normalize specs (array or object) into a list of display strings.
const specEntries = computed(() => {
  const s = product.value?.specs
  if (!s) return []
  if (Array.isArray(s)) {
    return s.map((x) =>
      typeof x === 'string'
        ? x
        : `${x.label || x.key || x.name || ''}${x.value != null ? ': ' + x.value : ''}`
    )
  }
  if (typeof s === 'object') {
    return Object.entries(s).map(([k, v]) => `${k}: ${v}`)
  }
  return []
})

async function load() {
  loading.value = true
  added.value = false
  imgError.value = false
  try {
    product.value = await getProduct(route.params.id)
  } catch (e) {
    product.value = null
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)

function addToCart() {
  if (!product.value) return
  cart.addItem(product.value)
  added.value = true
  setTimeout(() => (added.value = false), 1500)
}

function askAI() {
  if (!product.value) return
  open(`我想了解一下「${product.value.name}」这个商品，能帮我介绍一下吗？`)
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 py-8">
    <button
      @click="router.back()"
      class="text-text-secondary hover:text-apple-blue transition mb-6 flex items-center gap-1 text-sm"
    >
      <svg
        class="w-4 h-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        stroke-width="2"
      >
        <path
          d="M15 19l-7-7 7-7"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      返回
    </button>

    <!-- Loading -->
    <div v-if="loading" class="grid md:grid-cols-2 gap-10">
      <div class="aspect-square bg-black/5 rounded-card animate-pulse"></div>
      <div class="space-y-4">
        <div class="h-8 bg-black/5 rounded animate-pulse"></div>
        <div class="h-6 w-1/3 bg-black/5 rounded animate-pulse"></div>
        <div class="h-24 bg-black/5 rounded animate-pulse"></div>
      </div>
    </div>

    <!-- Detail -->
    <div v-else-if="product" class="grid md:grid-cols-2 gap-8 md:gap-10">
      <div class="aspect-square rounded-card overflow-hidden bg-white shadow-card">
        <img
          v-if="product.image && !imgError"
          :src="product.image"
          :alt="product.name"
          @error="imgError = true"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          class="w-full h-full flex items-center justify-center bg-gradient-to-br from-apple-blue to-blue-400"
        >
          <span class="text-7xl font-bold text-white/90">{{
            (product.name || '?').charAt(0)
          }}</span>
        </div>
      </div>

      <div class="flex flex-col">
        <span
          v-if="product.category"
          class="text-sm text-text-secondary mb-2"
          >{{ product.category }}</span
        >
        <h1 class="text-3xl font-bold text-text-primary">{{ product.name }}</h1>
        <p class="mt-4 text-4xl font-bold text-apple-blue">¥{{ price }}</p>

        <div class="mt-6 space-y-1 text-sm">
          <div
            class="flex justify-between py-2.5 border-b border-black/5"
          >
            <span class="text-text-secondary">库存</span>
            <span class="text-text-primary">{{
              product.stock ?? product.inventory ?? '充足'
            }}</span>
          </div>
          <div
            v-if="specEntries.length"
            class="py-2.5 border-b border-black/5"
          >
            <span class="text-text-secondary">规格</span>
            <ul class="mt-2 space-y-1.5 text-text-primary">
              <li v-for="(s, i) in specEntries" :key="i">{{ s }}</li>
            </ul>
          </div>
        </div>

        <p
          v-if="product.description"
          class="mt-6 text-text-secondary leading-relaxed"
        >
          {{ product.description }}
        </p>

        <div class="mt-8 flex flex-col sm:flex-row gap-3">
          <button
            @click="addToCart"
            class="flex-1 h-12 rounded-btn bg-apple-blue text-white font-medium hover:opacity-90 transition active:scale-95"
          >
            {{ added ? '已加入购物车' : '加入购物车' }}
          </button>
          <button
            @click="askAI"
            class="h-12 px-6 rounded-btn border border-apple-blue text-apple-blue font-medium hover:bg-apple-blue/5 transition"
          >
            问 AI
          </button>
        </div>
      </div>
    </div>

    <!-- Not found -->
    <div v-else class="text-center py-20 text-text-secondary">
      <p class="text-lg">商品不存在或已下架</p>
      <router-link
        to="/"
        class="inline-block mt-6 px-6 h-11 leading-[44px] rounded-btn bg-apple-blue text-white font-medium hover:opacity-90 transition"
        >返回首页</router-link
      >
    </div>
  </div>
</template>
