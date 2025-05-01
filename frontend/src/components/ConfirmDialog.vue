<template>
  <Dialog
    :open="open"
    class="relative z-50"
    @close="open = false"
  >
    <div class="fixed inset-0 bg-black/30" aria-hidden="true" />
    <div class="fixed inset-0 flex w-screen items-center justify-center p-4">
      <DialogPanel class="modal-box opacity-100">
        <DialogTitle>
          <h3 class="font-bold text-lg">
            {{ confirmHeader }}
          </h3>
        </DialogTitle>
        <p class="py-4">{{ confirmMessage }}</p>
        <div class="modal-action">
          <button
            :disabled="loading"
            class="btn btn-soft"
            @click="open = false"
          >
            Cancel
          </button>
          <button
            :disabled="loading"
            type="submit"
            class="btn btn-soft btn-warning"
            @click="onConfirm"
          >
            <span
              v-if="loading"
              class="loading loading-spinner"
            />
            {{ confirmAction ?? 'Confirm' }}
          </button>
        </div>
      </DialogPanel>
    </div>
  </Dialog>
</template>

<script setup>
import { reactive, ref, toRef, onBeforeMount, nextTick } from 'vue';
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import emitter from "../utilities/emitter.js";

const open = ref(false);

const confirmHeader = ref(null);
const confirmMessage = ref(null);
const confirmAction = ref(null);
const onConfirmFn = ref(null);

onBeforeMount(() => {
  emitter.on('show-confirm-dialog', (event) => {
    confirmHeader.value = event.confirmHeader;
    confirmMessage.value = event.confirmMessage;
    confirmAction.value = event.confirmAction;
    onConfirmFn.value = event.onConfirmFn;
    
    open.value = true;
  })
})

const initializing = ref(false);
const loading = ref(false);

const onConfirm = async () => {
  try {
    loading.value = true;
    await onConfirmFn.value();
    open.value = false;
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>