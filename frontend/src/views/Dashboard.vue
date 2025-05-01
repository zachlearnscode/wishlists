<template>
  <div class="flex flex-col gap-2 justify-center center p-3 md:w-2xl mx-auto">
    <button
      class="btn btn-block btn-soft btn-primary"
      @click="emitter.emit('show-create-wishlist-dialog')"
    >
      <PlusCircleIcon class="size-5"/>
      Create  a Wishlist
    </button>
    <div
      v-if="lists?.length"
      v-for="list in lists"
      :key="list.id"
      class="card w-96/100 shadow-sm w-full"
    >
      <RouterLink :to="`/wishlist/${list.id}`">
        <div class="card-body">
          <h2 class="card-title">
            {{ list.title }}
          </h2>
          <div class="flex gap-2">
            <span>Recipient: {{ list.recipient_name }}</span>
            <span>Contributors: {{ list.users.length }}</span>
          </div>
        </div>
      </RouterLink>
    </div>
    <div v-else class="card card-dash border-dashed border-3 w-full">
      <div class="card-body mx-auto opacity-40">
        <h2 class="card-title">
          Your wishlists will appear here
        </h2>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeMount } from 'vue';
import { useAuthStore } from "../stores/auth"
import { PlusCircleIcon } from '@heroicons/vue/24/outline';
import emitter from "../utilities/emitter"

const store = useAuthStore()

const lists = ref(null);
onBeforeMount(async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/users/${store.wishlistsUser.id}/wishlists`);
    const data = await res.json();

    lists.value = data;
  } catch (err) {
    console.error(err)
  }
})
</script>