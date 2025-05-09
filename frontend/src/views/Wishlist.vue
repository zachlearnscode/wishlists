<template>
  <div class="flex justify-center center p-3 md:w-2xl mx-auto">
    <span v-if="loading" class="loading loading-dots loading-md"></span>
    <div v-else class="w-full">
      <div class="flex justify-between">
        <h1 class="text-xl font-bold mr-auto">
          {{ wishlist.title }}
        </h1>
        <div class="flex">
          <div class="tooltip tooltip-bottom" data-tip="Add Item">
            <button
              class="btn btn-circle btn-ghost"
              @click="emitter.emit('show-add-item-modal', { wishlistId: id })"
            >
              <PlusCircleIcon class="size-6"/>
            </button>
          </div>
          <div class="tooltip tooltip-bottom" data-tip="Copy Invite">
            <button
              :class="confirmed ? 'btn-success' : 'btn-ghost'"
              class="btn btn-circle"
              @click="onCopyInviteLinkBtnClick"
            >
              <Transition name="fade" mode="out-in">
                <component
                  :is="confirmed ? CheckIcon : EnvelopeIcon"
                  :key="confirmed"
                  class="size-6"
                />
              </Transition>
            </button>
          </div>
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
                    @click="emitter.emit('show-manage-wishlist-dialog', { wishlistId: wishlist.id })"
                  >
                    <div class="flex align-center gap-1">
                      <AdjustmentsHorizontalIcon class="size-5 my-auto" />
                      Manage
                    </div>
                  </PopoverButton>
                  <PopoverButton
                    class="text-left cursor-pointer px-3"
                    @click="onLeaveBtnClick"
                  >
                    <div class="flex align-center gap-1">
                      <ArrowLeftStartOnRectangleIcon class="size-5 my-auto" />
                      Leave
                    </div>
                  </PopoverButton>
                </div>
              </PopoverPanel>
            </transition>
          </Popover>
        </div>
      </div>
      <ul class="list">
        <li class="p-4 pb-2 opacity-60 tracking-wide">Items</li>
        <li
          v-if="items?.length"
          v-for="(item, index) in items"
          :key="item.id"
          class="list-row"
        >
          <div class="text-4xl font-thin opacity-30 tabular-nums">
            {{ String(index + 1).padStart(2, '0') }}
          </div>
          <div class="flex-col-grow">
            <a
              v-if="item.url"
              :href="item.url"
              target="_blank"
              rel="noopener noreferrer"
              class="link link-info flex align-center gap-1"
            >
              {{ item.name }}
              <ArrowUpRightIcon class="size-3 my-auto" />
            </a>
            <div v-else>{{ item.name }}</div>
            <div class="flex gap-2 text-xs uppercase font-semibold opacity-60">
              {{ item.description }}
            </div>
          </div>
          <div class="list-col-wrap flex gap-1">
            <div class="flex gap-1 items-center">
              <LightBulbIcon class="size-4"/>
              {{ item.added_by.id == store.wishlistsUser.id ? 'You' : item.added_by_name }}
              <button
                v-if="item.added_by.id == store.wishlistsUser.id"
                class="btn btn-xs btn-outline"
                @click="emitter.emit('show-add-item-modal',  { wishlistId: id , editItemId: item.id })"
              >
                Edit
              </button>
            </div>
            <div class="flex gap-1 items-center">
              <HandRaisedIcon class="size-4"/>
              <span>{{ item.claimed_by?.id == store.wishlistsUser.id ? 'You' : (item.claimed_by?.name ?? '—') }}</span>
              <button
                v-if="!item.claimed_by || store.wishlistsUser.id == item.claimed_by.id"
                class="btn btn-xs btn-outline"
                @click="onClaimBtnClick(item.id, !item.claimed_by?.id)"
              >
                {{ `${item.claimed_by ? 'Unc' : 'C'}laim` }}
              </button>
            </div>
            <div class="flex gap-1 items-center">
              <GiftIcon class="size-4"/>
              <span>{{ item.acquired_by?.id == store.wishlistsUser.id ? 'You' : (item.acquired_by?.name ?? '—') }}</span>
              <button
                v-if="!item.acquired_by || store.wishlistsUser.id == item.acquired_by.id"
                class="btn btn-xs btn-outline"
                @click="onAcquireBtnClick(item.id, !item.acquired_by?.id)"
              >
                {{`${item.acquired_by ? 'Unm' : 'M'}ark as acquired`}}
              </button>
            </div>
          </div>
          <div>
            <div v-if="item.acquired_by" class="badge badge-soft badge-success ml-auto">Acquired</div>
            <div v-else-if="item.claimed_by" class="badge badge-soft badge-info ml-auto">Claimed</div>
            <div v-else class="badge badge-soft badge-error ml-auto">Unclaimed</div>
          </div>
        </li>
        <li v-else>
          <div class="card card-dash border-dashed border-3 w-full">
            <div class="card-body flex flex-col items-center">
              <h2 class="card-title opacity-40">
                Items will appear here
              </h2>
              <button
                class="btn btn-sm btn-wide btn-soft opacity-100 w-64"
                @click="emitter.emit('show-add-item-modal', { wishlistId: id })"
              >
                <PlusCircleIcon class="size-6"/>
                Add an item
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onBeforeMount, onMounted } from 'vue'
import { useRouter } from "vue-router"
import {
  Popover,
  PopoverButton,
  PopoverPanel
} from "@headlessui/vue"
import { AdjustmentsHorizontalIcon, EyeIcon, PlusCircleIcon, ArrowLeftStartOnRectangleIcon, Cog6ToothIcon, ArrowUpRightIcon, PencilSquareIcon, UserIcon, LightBulbIcon, HandRaisedIcon, GiftIcon, EnvelopeIcon, CheckIcon } from '@heroicons/vue/24/outline';
import WishlistSettingsPopover from "../components/WishlistSettingsPopover.vue";
import emitter from "../utilities/emitter.js"
import { useAuthStore } from "../stores/auth"
import api from "../api/axios"

const props = defineProps({
  id: String,
  required: true
})

const router = useRouter()
const store = useAuthStore()

const loading = ref(true);
const wishlist = ref(null);
const owner = computed(() => wishlist.value?.users.find(({ role }) => role == 'owner'))
const users = ref(null);
const items = ref(null);

onBeforeMount(() => {
  emitter.on('add-item-modal-success', async ({ action, data }) => {
    if (action == 'post') items.value.push(data);
    else if (action == 'put') {
      const itemIdx = items.value.findIndex(({ id }) => id == data.id);
      items.value[itemIdx] = data;
    } else {
      const res = await api(`/wishlists/${props.id}/items`)
      items.value = res.data
    }
  })
})

onMounted(async () => {
  try {
    const res = await Promise.allSettled([
      api(`/wishlists/${props.id}`),
      api(`/wishlists/${props.id}/users`),
      api(`/wishlists/${props.id}/items`)
    ])

    const refs = [wishlist, users, items];
    refs.forEach((r, i) => r.value = res[i].value.data);
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
})

const confirmed = ref(false);
const onCopyInviteLinkBtnClick = async () => {
  const { origin } = window.location;
  const inviteLink = `${origin}?invite=${wishlist.value.invitation_id}`
  await navigator.clipboard.writeText(inviteLink);
  confirmed.value = true;
  setTimeout(() => confirmed.value = false, 500)
}

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

const onClaimBtnClick = async (itemId, isClaiming) => {
  try {
    const res = await api.put(`/items/${itemId}/${isClaiming ? 'claim' : 'unclaim'}`)
    const itemIdx = items.value.findIndex(({ id }) => id == res.data.id);
    items.value[itemIdx] = res.data;
  } catch (err) {
    console.error(err)
  }
}

const onAcquireBtnClick = async (itemId, isAcquiring) => {
  try {
    const res = await api.put(`/items/${itemId}/${isAcquiring ? 'acquire' : 'unacquire'}`,)
    const itemIdx = items.value.findIndex(({ id }) => id == res.data.id);
    items.value[itemIdx] = res.data;
  } catch (err) {
    console.error(err)
  }
}
</script>