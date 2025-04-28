<template>
  <div class="flex justify-center center p-3">
    <span v-if="loading" class="loading loading-dots loading-md"></span>
    <div v-else class="w-full md:w-2xl">
      <div class="flex justify-between">
        <h1 class="text-xl font-bold mr-auto">
          {{ wishlist.title }}
        </h1>
        <div class="flex">
          <button
            class="btn btn-circle btn-ghost"
            @click="emitter.emit('show-add-item-modal', { wishlistId: id })"
          >
            <PlusCircleIcon class="size-6"/>
          </button>
          <div class="tooltip tooltip-bottom" data-tip="Leave">
            <button
              class="btn btn-circle btn-ghost"
              @click="onLeaveBtnClick"
            >
              <ArrowLeftStartOnRectangleIcon class="size-6"/>
            </button>
          </div>
          <div class="tooltip tooltip-bottom" data-tip="Manage">
            <button class="btn btn-circle btn-ghost">
              <Cog6ToothIcon class="size-6"/>
            </button>
          </div>
        </div>
      </div>
      <ul class="list">
        <li class="p-4 pb-2 opacity-60 tracking-wide">Items</li>
        <li v-for="(item, index) in items" :key="item.id" class="list-row">
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
          <div class="list-col-wrap flex flex-col sm:flex-row gap-1">
            <div class="flex gap-1 items-center">
              <LightBulbIcon class="size-4"/>
              {{ item.added_by_id }}
              <button
                v-if="item.added_by_id == user.id || true"
                class="btn btn-xs btn-outline"
                @click="emitter.emit('show-add-item-modal',  { wishlistId: id , editItemId: item.id })"
              >
                Edit
              </button>
            </div>
            <div class="flex gap-1 items-center">
              <HandRaisedIcon class="size-4"/>
              <span v-if="item.claimed_by_id">{{ item.claimed_by_id }}</span>
              <button
                v-if="!item.claimed_by_id || user.id == item.claimed_by_id"
                class="btn btn-xs btn-outline"
                @click="onClaimBtnClick(item.id, !item.claimed_by_id)"
              >
                {{ `${item.claimed_by_id ? 'Unc' : 'C'}laim` }}
              </button>
            </div>
            <div class="flex gap-1 items-center">
              <GiftIcon class="size-4"/>
              <span v-if="item.acquired_by_id">{{ item.acquired_by_id }}</span>
              <button
                v-if="!item.acquired_by_id || user.id == item.acquired_by_id"
                class="btn btn-xs btn-outline"
                @click="onAcquireBtnClick(item.id, !item.acquired_by_id)"
              >
                {{`${item.acquired_by_id ? 'Unm' : 'M'}ark as acquired`}}
              </button>
            </div>
          </div>
          <div>
            <div v-if="item.acquired_by_id" class="badge badge-soft badge-success ml-auto">Acquired</div>
            <div v-else-if="item.claimed_by_id" class="badge badge-soft badge-info ml-auto">Claimed</div>
            <div v-else class="badge badge-soft badge-error ml-auto">Unclaimed</div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onBeforeMount, onMounted } from 'vue'
import { EyeIcon, PlusCircleIcon, ArrowLeftStartOnRectangleIcon, Cog6ToothIcon, ArrowUpRightIcon, PencilSquareIcon, UserIcon, LightBulbIcon, HandRaisedIcon, GiftIcon } from '@heroicons/vue/24/outline';
import AddItemModal from "../components/AddItemModal.vue";
import emitter from "../utilities/emitter.js"

const props = defineProps({
  id: String,
  required: true
})

const user = reactive({id: 3})

const loading = ref(true);
const wishlist = ref(null);
const users = ref(null);
const items = ref(null);

onBeforeMount(() => {
  emitter.on('add-item-modal-success', ({ action, data }) => {
    if (action == 'add') items.value.push(data);
    else if (action == 'edit') {
      const itemIdx = items.value.findIndex(({ id }) => id == data.id);
      items.value[itemIdx] = data;
    }
  })
})

onMounted(async () => {
  try {
    const response = await Promise.allSettled([
      fetch(`${import.meta.env.VITE_API_URL}/wishlists/${props.id}`),
      fetch(`${import.meta.env.VITE_API_URL}/wishlists/${props.id}/users`),
      fetch(`${import.meta.env.VITE_API_URL}/wishlists/${props.id}/items`)
    ])

    const refs = [wishlist, users, items];
    response.forEach(async (res, i) => refs[i].value = await res.value.json())
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
})

const onLeaveBtnClick = () => {
  emitter.emit('show-confirm-modal', {
    confirmHeader: 'Leave List?',
    confirmMessage: 'Are you sure you want to leave?',
    confirmAction: 'Leave',
    onConfirmFn: async () => {
      await fetch(`${import.meta.env.VITE_API_URL}/wishlists/${props.id}/users/${user.id}`, { method: 'DELETE' })
    }
  })
}

const onClaimBtnClick = async (itemId, isClaiming) => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/items/${itemId}/${isClaiming ? 'claim' : 'unclaim'}`, { method: "PUT" })
    const data = await res.json()

    const itemIdx = items.value.findIndex(({ id }) => id == data.id);
    items.value[itemIdx] = data;
  } catch (err) {
    console.error(err)
  }
}

const onAcquireBtnClick = async (itemId, isAcquiring) => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/items/${itemId}/${isAcquiring ? 'acquire' : 'unacquire'}`, { method: "PUT" })
    const data = await res.json()

    const itemIdx = items.value.findIndex(({ id }) => id == data.id);
    items.value[itemIdx] = data;
  } catch (err) {
    console.error(err)
  }
}
</script>