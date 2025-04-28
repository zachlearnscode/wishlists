<template>
  <div class="flex justify-center">
    <div
      v-for="list in lists"
      :key="list.id"
      class="card w-96/100 shadow-sm p-"
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
  </div>
</template>

<script setup>
import { ref, onBeforeMount } from 'vue';

const lists = ref(null);
onBeforeMount(async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/users/1/wishlists`);
    const data = await res.json();

    lists.value = data;
  } catch (err) {
    console.error(err)
  }
})
</script>