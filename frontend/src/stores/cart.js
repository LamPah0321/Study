import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'ai-mall-cart'

function loadCart() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch (e) {
    return []
  }
}

export const useCartStore = defineStore('cart', () => {
  const items = ref(loadCart())

  const totalPrice = computed(() =>
    items.value.reduce((sum, i) => sum + Number(i.product.price) * i.quantity, 0)
  )

  const totalCount = computed(() =>
    items.value.reduce((sum, i) => sum + i.quantity, 0)
  )

  function addItem(product, qty = 1) {
    const existing = items.value.find((i) => i.product.id === product.id)
    if (existing) {
      existing.quantity += qty
    } else {
      items.value.push({ product, quantity: qty })
    }
  }

  function removeItem(productId) {
    items.value = items.value.filter((i) => i.product.id !== productId)
  }

  function updateQuantity(productId, qty) {
    const item = items.value.find((i) => i.product.id === productId)
    if (!item) return
    if (qty <= 0) {
      removeItem(productId)
    } else {
      item.quantity = qty
    }
  }

  function clear() {
    items.value = []
  }

  // Persist to localStorage on any change.
  watch(
    items,
    (val) => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
      } catch (e) {
        /* ignore quota errors */
      }
    },
    { deep: true }
  )

  return {
    items,
    totalPrice,
    totalCount,
    addItem,
    removeItem,
    updateQuantity,
    clear,
  }
})
