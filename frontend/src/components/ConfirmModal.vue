<template>
  <Teleport to="body">
    <dialog ref="confirmModal" class="modal">
      <div class="modal-box">
        <h3 class="text-lg font-bold pb-5">{{ confirmHeader }}</h3>
        <p>{{ confirmMessage }}</p>
        <div class="modal-action">
          <form method="dialog">
            <button
              :disabled="loading"
              class="btn btn-soft"
            >
              Cancel
            </button>
          </form>
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
      </div>
    </dialog>
  </Teleport>
</template>

<script setup>
import { reactive, ref, toRef, onBeforeMount, nextTick } from 'vue';
import emitter from "../utilities/emitter.js";

const confirmHeader = ref(null);
const confirmMessage = ref(null);
const confirmAction = ref(null);
const onConfirmFn = ref(null);

onBeforeMount(() => {
  emitter.on('show-confirm-modal', (event) => {
    confirmHeader.value = event.confirmHeader;
    confirmMessage.value = event.confirmMessage;
    confirmAction.value = event.confirmAction;
    onConfirmFn.value = event.onConfirmFn;
    
    confirmModal.value?.showModal();
  })
})

const initializing = ref(false);
const loading = ref(false);

const confirmModal = ref(null);

const onConfirm = async () => {
  try {
    loading.value = true;
    await onConfirmFn.value();
    confirmModal.value?.close();
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>