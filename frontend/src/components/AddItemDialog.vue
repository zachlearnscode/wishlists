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
            {{ !editItemId ? 'Add' : 'Edit' }} Item
          </h3>
        </DialogTitle>
        <form
          :id="form.formId"
          class="flex flex-col gap-2 py-4"
          @submit.prevent="onSubmit"
        >
          <label
            :class="{ 'input-error': toValue(form.errors).name }"
            class="input w-full"
          >
            Name
            <input
              v-model="name"
              v-bind="nameAttrs"
              :disabled="loading"
              type="text"
            />
            <span class="badge badge-neutral badge-xs">Required</span>
          </label>
          <span
            v-if="toValue(form.errors).name"
            class="text-error text-xs -mt-1.5"
          >
            {{ toValue(form.errors).name }}
          </span>
          <label
            :class="{ 'input-error': toValue(form.errors).description }"
            class="input w-full mt-1"
          >
            Description
            <input
              v-model="description"
              v-bind="descriptionAttrs"
              :disabled="loading"
              type="text"
              maxlength="50"
            />
            <span class="text-xs">{{ description?.length ?? 0 }}/50</span>
          </label>
          <span
            v-if="toValue(form.errors).description"
            class="text-error text-xs -mt-1.5"
          >
            {{ toValue(form.errors).description }}
          </span>
          <label
            :class="{ 'input-error': toValue(form.errors).url }"
            class="input w-full mt-1"
          >
            URL
            <input
              v-model="url"
              v-bind="urlAttrs"
              :disabled="loading"
              type="url"
            />
          </label>
          <span
            v-if="toValue(form.errors).url"
            :class="{ 'input-error': toValue(form.errors).url }"
            class="text-error text-xs -mt-1.5"
          >
            {{ toValue(form.errors).url }}
          </span>
        </form>
        <div class="modal-action">
          <button
            for="add_item_modal"
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
import { reactive, ref, toRef, toValue, onBeforeMount, onMounted } from 'vue';
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { PlusCircleIcon } from '@heroicons/vue/24/outline';
import { useForm } from 'vee-validate';
import * as yup from 'yup';
import emitter from "../utilities/emitter.js";

const open = ref(false);

const wishlistId = ref(null);
const editItemId = ref(null);

const initializing = ref(false);
const loading = ref(false);

onBeforeMount(() => {
  emitter.on("show-add-item-modal", (event) => {
    wishlistId.value = event.wishlistId;
    open.value = true;
  })
})

const validationSchema = yup.object({
  name: yup.string().required('Name is required'),
  description: yup.string().max(50, "Must be 50 characters or fewer"),
  url: yup.string().url('Enter a valid URL')
})

const form = useForm({ validationSchema });

const fieldConfig = reactive({
  validateOnBlur: true,
  validateOnChange: false,
  validateOnInput: false,
  validateOnModelUpdate: false
})

const [name, nameAttrs] = form.defineField('name', fieldConfig);
const [description, descriptionAttrs] = form.defineField('description', fieldConfig);
const [url, urlAttrs] = form.defineField('url', fieldConfig);

const onSubmit = form.handleSubmit(async (values) => {
  try {
    loading.value = true;

    const { name, description, url } = values
    const body = { name, description, url };

    if (!editItemId.value) body.added_by_id = 2;

    const res = await fetch(`${import.meta.env.VITE_API_URL}/${!editItemId.value ? `wishlists/${wishlistId.value}/item` : `items/${editItemId.value}` }`, {
      method: !editItemId.value ? 'POST' : 'PUT',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json()
    emitter.emit('add-item-modal-success', { action: !editItemId.value ? 'add' : 'edit', data })

    open.value = false;
  } catch (err) {
    console.error(error)
  } finally {
    loading.value = false
  }
});

const onClose = () => {
  open.value = false;
  form.resetForm()
}
</script>