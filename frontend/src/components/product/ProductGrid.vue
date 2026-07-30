<script setup>
import ProductCard from './ProductCard.vue'

defineProps({
  products: { type: Array, default: () => [] },
})
</script>

<template>
  <div
    v-if="products.length === 0"
    class="text-center py-20 text-text-secondary"
  >
    <svg
      class="w-12 h-12 mx-auto mb-4 text-text-secondary/40"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      stroke-width="1.5"
    >
      <path
        d="M4 7h16M9 7V5a1 1 0 011-1h4a1 1 0 011 1v2M6 7l1 13a1 1 0 001 1h8a1 1 0 001-1l1-13"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <p class="text-lg">暂无商品</p>
  </div>
  <div
    v-else
    class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
  >
    <ProductCard v-for="p in products" :key="p.id" :product="p" />
  </div>
</template>
