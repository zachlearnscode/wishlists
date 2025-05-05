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
        <button v-else @click="store.signOut" class="cursor-pointer">Sign Out</button>
      </div>

      <!-- Mobile Nav with Headless UI Popover -->
      <Popover v-slot="{ open }" as='nav' class="relative md:hidden">
        <PopoverButton class="btn btn-ghost p-0 text-gray-600">
          <Bars3Icon class="size-7" />
        </PopoverButton>

        <transition
          enter="transition ease-out duration-150"
          enter-from="opacity-0 scale-95"
          enter-to="opacity-100 scale-100"
          leave="transition ease-in duration-100"
          leave-from="opacity-100 scale-100"
          leave-to="opacity-0 scale-95"
        >
          <PopoverPanel class="absolute right-0 mt-2 w-auto origin-top-right bg-white border border-gray-200 rounded-md shadow-lg z-50 focus:outline-none">
            <div class="flex flex-col justify-start py-2 px-3 space-y-1 whitespace-nowrap">
              <PopoverButton as="template" to="/dashboard" class="text-left cursor-pointer">
                <RouterLink to="/dashboard" class="text-left cursor-pointer">Dashboard</RouterLink>
              </PopoverButton>
              <PopoverButton as="template">
                <RouterLink to="/account" class="text-left cursor-pointer">My Account</RouterLink>
              </PopoverButton>
              <PopoverButton v-if="!store.isAuthenticated" as="template">
                <RouterLink  to="/sign-in" class="text-left cursor-pointer">Sign In</RouterLink>
              </PopoverButton>
              <PopoverButton
                v-else
                class="text-left cursor-pointer"
                @click="handleSignOut"
              >
                Sign Out
              </PopoverButton>
            </div>
          </PopoverPanel>
        </transition>
      </Popover>
    </nav>

    <router-view />

    <CreateWishlistDialog />
    <ManageWishlistDialog />
    <AddItemDialog />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref } from "vue"
import {
  Popover,
  PopoverButton,
  PopoverPanel
} from "@headlessui/vue"
import { Bars3Icon } from "@heroicons/vue/24/outline"
import { useAuthStore } from "./stores/auth"
import CreateWishlistDialog from "./components/CreateWishlistDialog.vue"
import ManageWishlistDialog from "./components/ManageWishlistDialog.vue"
import AddItemDialog from "./components/AddItemDialog.vue"
import ConfirmDialog from "./components/ConfirmDialog.vue"

const store = useAuthStore()

const mobileLink =
  "block w-full px-4 py-2 text-sm text-gray-700 rounded hover:bg-gray-100 transition"

const closePopover = () => {
  const activeEl = document.activeElement
  if (activeEl && typeof activeEl.blur === "function") activeEl.blur()
}

const handleSignOut = async () => {
  await store.signOut()
  closePopover()
}
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
