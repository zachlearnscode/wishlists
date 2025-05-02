<template>
  <Dialog
    :open="open"
    class="relative z-50"
    @close="onClose"
  >
    <div class="fixed inset-0 bg-black/30" aria-hidden="true" />
    <div class="fixed inset-0 flex w-screen items-center justify-center p-4">
      <DialogPanel class="modal-box opacity-100">
        <DialogTitle>
          <h3 class="font-bold text-lg">
            Create Wishlist
          </h3>
        </DialogTitle>
        <form
          :id="form.formId"
          class="gap-2 py-4"
          @submit.prevent="onSubmit"
        >
          <label
            :class="{ 'input-error': toValue(form.errors).title }"
            class="input w-full"
          >
            Title
            <input
              v-model="title"
              v-bind="titleAttrs"
              :disabled="loading"
              type="text"
            />
          </label>
          <span
            v-if="toValue(form.errors).title"
            class="text-error text-xs -mt-1.5"
          >
            {{ toValue(form.errors).title }}
          </span>
          <label
            :class="{ 'input-error': toValue(form.errors).recipientName }"
            class="input w-full mt-1"
          >
            Recipient Name
            <input
              v-model="recipientName"
              v-bind="recipientNameAttrs"
              :disabled="loading"
              type="text"
            />
          </label>
          <span
            v-if="toValue(form.errors).recipientName"
            class="text-error text-xs -mt-1.5"
          >
            {{ toValue(form.errors).recipientName }}
          </span>
        </form>
        <div class="modal-action">
          <button
            for="create_wishlist_modal"
            class="btn btn-soft"
            @click="onClose"
          >
            Cancel
          </button>
          <button
            :form="form.formId"
            :disabled="loading"
            type="submit"
            class="btn btn-soft btn-primary"
          >
            <span
              v-if="loading"
              class="loading loading-spinner"
            />
            Submit
          </button>
        </div>
      </DialogPanel>
    </div>
  </Dialog>
</template>

<script setup>
import { reactive, ref, toRef, toValue, onBeforeMount } from 'vue';
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { PlusCircleIcon } from '@heroicons/vue/24/outline';
import { useForm } from 'vee-validate';
import * as yup from 'yup';
import { useAuthStore } from "../stores/auth"
import emitter from "../utilities/emitter.js";
import api from "../api/axios"

const store = useAuthStore()

const open = ref(false)

const initializing = ref(false);
const loading = ref(false);

onBeforeMount(() => {
  emitter.on("show-create-wishlist-dialog", () => open.value = true)
})

const validationSchema = yup.object({
  title: yup.string().required('Title is required'),
  recipientName: yup.string().required('Recipient Name is required')
})

const form = useForm({ validationSchema });

const fieldConfig = reactive({
  validateOnBlur: true,
  validateOnChange: false,
  validateOnInput: false,
  validateOnModelUpdate: false
})

const [title, titleAttrs] = form.defineField('title', fieldConfig);
const [recipientName, recipientNameAttrs] = form.defineField('recipientName', fieldConfig);

const onSubmit = form.handleSubmit(async (values) => {
  try {
    loading.value = true;

    const { title, recipientName } = values;
    const data = { title, recipient_name: recipientName };
    const res = await api.post('/wishlists', data)

    emitter.emit('create-wishlist-success', { wishlist: res.data })
    open.value = false;
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false;
  }


});

const onClose = () => {
  open.value = false;
  form.resetForm();
}
</script>