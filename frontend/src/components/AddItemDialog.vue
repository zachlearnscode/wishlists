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
        <div
          :class="editItemId ? 'justify-between' : 'justify-end'"
          class="modal-action"
        >
          <button
            v-if="editItemId"
            class="btn btn-soft btn-error"
            @click="onDeleteItemClick"
          >
            Delete Item
          </button>
          <div class="flex gap-1">
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
import api from "../api/axios"

const open = ref(false);

const wishlistId = ref(null);
const editItemId = ref(null);

const initializing = ref(false);
const loading = ref(false);

onBeforeMount(() => {
  emitter.on("show-add-item-modal", async (event) => {
    wishlistId.value = event.wishlistId;
    if (event.editItemId) {
      editItemId.value = event.editItemId;
      try {
        const res = await api(`/items/${editItemId.value}`)
        const data = res.data

        data.name && (name.value = data.name )
        data.description && (description.value = data.description)
        data.url && (url.value = data.url)
      } catch (err) {
        console.error(err)
      }
    }
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
    const data = { name, description, url };

    const method = editItemId.value ? 'put' : 'post'
    const res = await (
      method == 'post' ?
        api.post(`/wishlists/${wishlistId.value}/item`, data) :
        api.put(`/items/${editItemId.value}`, data)
      );

    emitter.emit('add-item-modal-success', { action: method, data: res.data })
    open.value = false;
  } catch (err) {
    console.error(error)
  } finally {
    loading.value = false
  }
});

const onDeleteItemClick = async () => {
  try {
    loading.value = true
    await api.put(`/items/${editItemId.value}`, { active: false })
    emitter.emit('add-item-modal-success', { action: 'remove' })
    open.value = false;
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const onClose = () => {
  open.value = false;
  form.resetForm()
}
</script>