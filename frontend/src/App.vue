<template>
  <div>
    <nav class="bg-white border-b border-gray-200 shadow-sm px-4 py-3 flex justify-between items-center">
      <!-- Logo -->
      <div class="text-xl font-semibold text-gray-800">
        Wishlists
      </div>

      <!-- Desktop Links -->
      <div class="hidden md:flex space-x-6">
        <RouterLink to="/dashboard" class="nav-link" exact>Dashboard</RouterLink>
        <RouterLink to="/invitations" class="nav-link">Invitations</RouterLink>
        <RouterLink to="/account" class="nav-link">Account</RouterLink>
      </div>

      <!-- Mobile Menu Button -->
      <button @click="showMenu = !showMenu" class="md:hidden text-gray-600 focus:outline-none">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2"
            viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
      </button>

      <!-- Mobile Menu -->
      <div v-if="showMenu" class="absolute top-full left-0 w-full bg-white border-t border-gray-200 mt-2 py-2 flex flex-col space-y-2 md:hidden z-50">
        <RouterLink to="/dashboard" class="mobile-link" exact>Dashboard</RouterLink>
        <RouterLink to="/invitations" class="mobile-link">Invitations</RouterLink>
        <RouterLink to="/account" class="mobile-link">Account</RouterLink>
      </div>
    </nav>
    <router-view></router-view>
  </div>
  <AddItemModal />
  <ConfirmModal />
</template>

<script setup>
import AddItemModal from "./components/AddItemModal.vue"
import ConfirmModal from "./components/ConfirmModal.vue"
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
