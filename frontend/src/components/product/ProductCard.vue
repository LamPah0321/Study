<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  product: { type: Object, required: true },
})

const router = useRouter()
const imgError = ref(false)

const showImage = computed(
  () => props.product.image && !imgError.value
)

const initial = computed(() => {
  const name = props.product.name || ''
  return name.charAt(0) || '?'
})

// Deterministic gradient chosen by product id, so each card is visually stable.
const gradient = computed(() => {
  const id = Number(props.product.id) || 0
  const hues = [
    'linear-gradient(135deg,#0071e3,#42a5f5)',
    'linear-gradient(135deg,#5856d6,#af52de)',
    'linear-gradient(135deg,#ff2d55,#ff9500)',
    'linear-gradient(135deg,#34c759,#30d158)',
    'linear-gradient(135deg,#ff9500,#ffcc00)',
    'linear-gradient(135deg,#af52de,#ff2d55)',
    'linear-gradient(135deg,#00c7be,#0071e3)',
    'linear-gradient(135deg,#5e5ce6,#bf5af2)',
  ]
  return hues[id % hues.length]
})

const price = computed(() => {
  const p = Number(props.product.price)
  return isNaN(p) ? '0.00' : p.toFixed(2)
})

function goDetail() {
  router.push(`/product/${props.product.id}`)
}
function onError() {
  imgError.value = true
}
</script>

<template>
  <div
    @click="goDetail"
    class="group cursor-pointer bg-white rounded-card shadow-card hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300 overflow-hidden"
  >
    <div class="aspect-square overflow-hidden">
      <img
        v-if="showImage"
        :src="product.image"
        :alt="product.name"
        @error="onError"
        loading="lazy"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center"
        :style="{ background: gradient }"
      >
        <span class="text-5xl font-bold text-white/90">{{ initial }}</span>
      </div>
    </div>
    <div class="p-5">
      <div v-if="product.category" class="mb-1.5">
        <span
          class="text-xs text-text-secondary bg-black/5 px-2 py-0.5 rounded-full"
          >{{ product.category }}</span
        >
      </div>
      <h3 class="text-text-primary font-medium text-base truncate">
        {{ product.name }}
      </h3>
      <p class="mt-2 text-apple-blue font-bold text-lg">¥{{ price }}</p>
    </div>
  </div>
</template>
