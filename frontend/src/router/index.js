import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomePage.vue'),
    meta: { title: 'AI 智能商城' },
  },
  {
    path: '/product/:id',
    name: 'product',
    component: () => import('../views/ProductDetail.vue'),
    meta: { title: '商品详情' },
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('../views/Cart.vue'),
    meta: { title: '购物车' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.afterEach((to) => {
  const base = 'AI Mall'
  document.title = to.meta.title ? `${to.meta.title} - ${base}` : base
})

export default router
