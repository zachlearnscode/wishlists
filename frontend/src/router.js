import { createWebHistory, createRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { watch } from 'vue'

import Root from './views/Root.vue'
import Dashboard from './views/Dashboard.vue'
import Wishlist from './views/Wishlist.vue'
import Account from './views/Account.vue'
import SignIn from './views/SignIn.vue'

const routes = [
  { path: '/', component: Root },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/wishlist/:id', component: Wishlist, props: true, meta: { requiresAuth: true } },
  { path: '/account/', component: Account, props: true, meta: { requiresAuth: true } },
  { path: '/sign-in', component: SignIn },
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