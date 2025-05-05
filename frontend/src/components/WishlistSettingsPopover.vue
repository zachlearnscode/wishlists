<template>
  <Popover v-slot="{ open }" class="relative">
    <div
      :class="{ tooltip: !open }"
      data-tip="Settings"
      class="tooltip-bottom"
    >
      <PopoverButton class="btn btn-circle btn-ghost">
        <Cog6ToothIcon class="size-6" />
      </PopoverButton>
    </div>

    <transition
      enter="transition ease-out duration-150"
      enter-from="opacity-0 scale-95"
      enter-to="opacity-100 scale-100"
      leave="transition ease-in duration-100"
      leave-from="opacity-100 scale-100"
      leave-to="opacity-0 scale-95"
    >
      <PopoverPanel class="absolute right-0 mt-2 w-auto origin-top-right bg-white border border-gray-200 rounded-md shadow-lg z-50 focus:outline-none">
        <div class="flex flex-col justify-start py-2 space-y-1 whitespace-nowrap">
          <PopoverButton
            v-if="owner.user_id == store.wishlistsUser.id"
            class="text-left cursor-pointer px-3"
          >
            Manage
          </PopoverButton>
          <PopoverButton class="text-left cursor-pointer px-3">
            Leave
          </PopoverButton>
        </div>
      </PopoverPanel>
    </transition>
  </Popover>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Popover,
  PopoverButton,
  PopoverPanel
} from "@headlessui/vue"
import { Cog6ToothIcon } from '@heroicons/vue/24/outline';
import emitter from "../utilities/emitter.js"
import { useAuthStore } from "../stores/auth.js"

const store = useAuthStore();

const props = defineProps({
  wishlist: {
    type: Object,
    required: true
  }
})

const owner = computed(() => props.wishlist.users.find(({ role }) => role == 'owner'))

const onLeaveBtnClick = () => {
  emitter.emit('show-confirm-dialog', {
    confirmHeader: 'Leave List?',
    confirmMessage: 'Are you sure you want to leave?',
    confirmAction: 'Leave',
    onConfirmFn: async () => {
      try {
        await api.delete(`/wishlists/${props.id}/user`)
        router.push('/dashboard');
      } catch (err) {
        console.error(err)
      }
    }
  })
}
</script>