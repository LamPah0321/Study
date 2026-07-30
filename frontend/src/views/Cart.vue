<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useCartStore } from '../stores/cart'
import { checkoutCart } from '../api'

const router = useRouter()
const cart = useCartStore()
const { items, totalPrice, totalCount } = storeToRefs(cart)

const checkingOut = ref(false)
const success = ref(false)

async function checkout() {
  if (items.value.length === 0 || checkingOut.value) return
  checkingOut.value = true
  try {
    const payload = items.value.map((i) => ({
      product_id: i.product.id,
      quantity: i.quantity,
    }))
    await checkoutCart(payload)
    success.value = true
    cart.clear()
    setTimeout(() => router.push('/'), 2000)
  } catch (e) {
    // error surfaced via interceptor
  } finally {
    checkingOut.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 py-8">
    <h1 class="text-3xl font-bold text-text-primary mb-8">购物车</h1>

    <!-- Success -->
    <div
      v-if="success"
      class="bg-white rounded-card shadow-card p-12 text-center"
    >
      <div
        class="w-16 h-16 mx-auto rounded-full bg-green-100 flex items-center justify-center mb-4"
      >
        <svg
          class="w-8 h-8 text-green-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          stroke-width="2.5"
        >
          <path
            d="M5 13l4 4L19 7"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>
      <p class="text-xl font-semibold text-text-primary">下单成功</p>
      <p class="text-text-secondary mt-2">即将返回首页...</p>
    </div>

    <!-- Empty -->
    <div
      v-else-if="items.length === 0"
      class="bg-white rounded-card shadow-card p-16 text-center"
    >
      <svg
        class="w-16 h-16 mx-auto mb-4 text-text-secondary/40"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        stroke-width="1.5"
      >
        <circle cx="9" cy="20" r="1.5" />
        <circle cx="18" cy="20" r="1.5" />
        <path
          d="M2.5 3h2.2l2.2 12.4a1.6 1.6 0 0 0 1.6 1.3h9.8a1.6 1.6 0 0 0 1.6-1.3L22 7H6"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <p class="text-text-secondary text-lg">购物车是空的</p>
      <router-link
        to="/"
        class="inline-block mt-6 px-6 h-11 leading-[44px] rounded-btn bg-apple-blue text-white font-medium hover:opacity-90 transition"
        >去逛逛</router-link
      >
    </div>

    <!-- Items -->
    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.product.id"
        class="bg-white rounded-card shadow-card p-4 flex items-center gap-4"
      >
        <div
          class="w-20 h-20 rounded-xl overflow-hidden bg-black/5 flex-shrink-0"
        >
          <img
            v-if="item.product.image"
            :src="item.product.image"
            :alt="item.product.name"
            class="w-full h-full object-cover"
          />
          <div
            v-else
            class="w-full h-full flex items-center justify-center bg-gradient-to-br from-apple-blue to-blue-400"
          >
            <span class="text-2xl font-bold text-white/90">{{
              (item.product.name || '?').charAt(0)
            }}</span>
          </div>
        </div>

        <div class="flex-1 min-w-0">
          <h3 class="text-text-primary font-medium truncate">
            {{ item.product.name }}
          </h3>
          <p class="text-apple-blue font-bold mt-1">
            ¥{{ Number(item.product.price).toFixed(2) }}
          </p>
        </div>

        <!-- Quantity stepper -->
        <div class="flex items-center gap-2">
          <button
            @click="cart.updateQuantity(item.product.id, item.quantity - 1)"
            class="w-8 h-8 rounded-btn border border-black/10 text-text-primary hover:bg-black/5 transition flex items-center justify-center"
            aria-label="减少"
          >
            <svg
              class="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              stroke-width="2.5"
            >
              <path d="M5 12h14" stroke-linecap="round" />
            </svg>
          </button>
          <span class="w-8 text-center text-text-primary">{{
            item.quantity
          }}</span>
          <button
            @click="cart.updateQuantity(item.product.id, item.quantity + 1)"
            class="w-8 h-8 rounded-btn border border-black/10 text-text-primary hover:bg-black/5 transition flex items-center justify-center"
            aria-label="增加"
          >
            <svg
              class="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              stroke-width="2.5"
            >
              <path d="M12 5v14M5 12h14" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <button
          @click="cart.removeItem(item.product.id)"
          class="text-text-secondary hover:text-red-500 transition p-2"
          aria-label="删除"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            stroke-width="1.8"
          >
            <path
              d="M4 7h16M9 7V5a1 1 0 011-1h4a1 1 0 011 1v2M6 7l1 13a1 1 0 001 1h8a1 1 0 001-1l1-13"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>

      <!-- Summary -->
      <div
        class="bg-white rounded-card shadow-card p-6 flex items-center justify-between sticky bottom-4"
      >
        <div>
          <p class="text-text-secondary text-sm">共 {{ totalCount }} 件商品</p>
          <p class="text-2xl font-bold text-text-primary mt-1">
            合计：<span class="text-apple-blue">¥{{ totalPrice.toFixed(2) }}</span>
          </p>
        </div>
        <button
          @click="checkout"
          :disabled="checkingOut"
          class="h-12 px-8 sm:px-10 rounded-btn bg-apple-blue text-white font-medium hover:opacity-90 transition active:scale-95 disabled:opacity-50"
        >
          {{ checkingOut ? '结算中...' : '结算' }}
        </button>
      </div>
    </div>
  </div>
</template>
