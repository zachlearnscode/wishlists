<template>
  <div>
    <nav class="bg-white border-b border-gray-200 shadow-sm px-4 py-3 flex justify-between items-center relative">
    <!-- Brand -->
    <RouterLink to="/" class="text-xl font-semibold text-gray-800">
      Wishlists
    </RouterLink>

    <!-- Desktop Nav -->
    <div class="hidden md:flex space-x-6 items-center">
      <RouterLink to="/dashboard" class="nav-link" exact>Dashboard</RouterLink>
      <RouterLink to="/account" class="nav-link">My Account</RouterLink>
      <RouterLink v-if="!store.isAuthenticated" to="/sign-in" class="nav-link">Sign In</RouterLink>
      <button v-else @click="store.signOut" class="btn nav-link">Sign Out</button>
    </div>

    <!-- Mobile Menu using Headless UI -->
    <Menu as="div" class="relative md:hidden">
      <MenuButton class="btn btn-ghost p-0 text-gray-600">
        <Bars3Icon class="size-7" />
      </MenuButton>
      <MenuItems class="absolute right-0 mt-2 w-auto origin-top-right rounded-md bg-white shadow-lg border border-gray-200 focus:outline-none z-50">
        <div class="flex flex-col py-2 px-3 space-y-1 whitespace-nowrap">
          <MenuItem v-slot="{ active }">
            <RouterLink :class="[mobileLink]" to="/dashboard">Dashboard</RouterLink>
          </MenuItem>
          <MenuItem v-slot="{ active }">
            <RouterLink :class="[mobileLink]" to="/account">My Account</RouterLink>
          </MenuItem>
          <MenuItem v-if="!store.isAuthenticated" v-slot="{ active }">
            <RouterLink :class="[mobileLink]" to="/sign-in">Sign In</RouterLink>
          </MenuItem>
          <MenuItem v-else v-slot="{ active }">
            <button
              :class="[mobileLink, 'text-left w-full cursor-pointer']"
              @click="store.signOut"
            >
              Sign Out
            </button>
          </MenuItem>
        </div>
      </MenuItems>
    </Menu>
  </nav>

    <router-view></router-view>
  </div>
  <CreateWishlistDialog />
  <AddItemDialog />
  <ConfirmDialog />


</template>

<script setup>
import { ref } from "vue";
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import { Bars3Icon } from '@heroicons/vue/24/outline';
import { useAuthStore } from "./stores/auth"
import CreateWishlistDialog from "./components/CreateWishlistDialog.vue"
import AddItemDialog from "./components/AddItemDialog.vue"
import ConfirmDialog from "./components/ConfirmDialog.vue"

const store = useAuthStore()

const showMenu = ref(false);
</script>


<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
