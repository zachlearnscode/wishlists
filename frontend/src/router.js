import { createWebHistory, createRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { watch } from 'vue'

import Root from './views/Root.vue'
import Dashboard from './views/Dashboard.vue'
import Wishlist from './views/Wishlist.vue'
import SignIn from './views/SignIn.vue'
import NotFound from './views/NotFound.vue'

const routes = [
  { path: '/', component: Root },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/wishlist/:id', component: Wishlist, props: true, meta: { requiresAuth: true } },
  { path: '/sign-in', component: SignIn },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const store = useAuthStore()

  // Wait until Firebase auth is initialized
  if (store.loading) {
    await new Promise((resolve) => {
      const unwatch = watch(
        () => store.loading,
        (newVal) => {
          if (newVal === false) {
            unwatch()
            resolve()
          }
        }
      )
    })
  }

  if (to.meta.requiresAuth && !store.isAuthenticated) return '/sign-in'
  else if (to.path === '/sign-in' && store.isAuthenticated) return '/dashboard'
})


export default router