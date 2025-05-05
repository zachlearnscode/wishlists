<template>
  <Dialog
    :open="open"
    @close="onClose"
    class="relative overflow-visible"
  >
    <div class="fixed inset-0 bg-black/30" aria-hidden="true" />
    <div class="fixed inset-0 flex w-screen items-center justify-center p-4">
      <DialogPanel class="modal-box opacity-100 relative overflow-visible">
        <DialogTitle>
          <h3 class="font-bold text-lg">
            Manage Wishlist
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
        <div class="modal-action flex justify-between">
          <Popover class="relative">
            <PopoverButton class="btn btn-soft btn-error">
              Close Wishlist
            </PopoverButton>

            <PopoverPanel
              v-slot="{ close }"
              class="absolute w-sm mt-2 p-3 bg-white border border-gray-200 rounded-md shadow-lg focus:outline-none"
            >
              <form
                id="close_wishlist_form"
                @submit.prevent="onCloseWishlistFormSubmit(close)"
              >
                Close this wishlist? This cannot be undone.
              </form>
              <div class="flex gap-1 mt-2 justify-end">
                <button class="btn btn-sm btn-soft" @click="close">Cancel</button>
                <button
                  type="submit"
                  form="close_wishlist_form"
                  class="btn btn-sm btn-error"
                >
                  Close
                </button>
              </div>
            </PopoverPanel>
          </Popover>
          <div class="flex gap-2">
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
              Save
            </button>
          </div>
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
import { useRouter } from "vue-router";
import {
  Popover,
  PopoverButton,
  PopoverPanel
} from "@headlessui/vue"
import * as yup from 'yup';
import { useAuthStore } from "../stores/auth"
import emitter from "../utilities/emitter.js";
import api from "../api/axios"

const router = useRouter()
const store = useAuthStore()

const open = ref(false)

const initializing = ref(false);
const loading = ref(false);

const wishlistId = ref(null)

onBeforeMount(() => {
  emitter.on("show-manage-wishlist-dialog", async (event) => {
    wishlistId.value = event.wishlistId;

    open.value = true;
    initializing.value = true;

    try {
      const res1 = await api(`/wishlists/${wishlistId.value}`)
      const data1 = res1.data;

      title.value = data1.title;
      recipientName.value = data1.recipient_name;
    } catch (err) {
      console.error(err)
    } finally {
      initializing.value = false;
    }
  })
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
    const res = await api.put(`/wishlists/${wishlistId.value}`, data)

    emitter.emit('edit-wishlist-success', { wishlist: res.data })
    open.value = false;
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false;
  }
});

const onCloseWishlistFormSubmit = async (closePopover) => {
  try {
    loading.value = true;
    const res = await api.patch(`/wishlists/${wishlistId.value}/deactivate`)
    loading.value = false
    open.value = false;
    router.push('/dashboard')
  } catch (err) {
    console.error(err)
  } finally {
    closePopover()
  }
}

const onClose = () => {
  open.value = false;
  form.resetForm();
}
</script>