import { createWebHistory, createRouter } from 'vue-router'

import Root from './views/Root.vue'
import Dashboard from './views/Dashboard.vue'
import Wishlist from './views/Wishlist.vue'

const routes = [
  { path: '/', component: Root },
  { path: '/dashboard', component: Dashboard },
  { path: '/wishlist/:id', component: Wishlist, props: true },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})