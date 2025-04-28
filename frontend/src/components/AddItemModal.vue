<template>
  <Teleport to="body">
    <dialog ref="addItemModal" class="modal">
      <div class="modal-box">
        <span v-if="initializing" class="loading loading-spinner" />
        <template v-else>
          <h3 class="text-lg font-bold pb-5">{{ !editItemId ? 'Add' : 'Edit' }} Item</h3>
          <form
            :id="form.formId"
            class="flex flex-col gap-2"
            @submit.prevent="onSubmit({ 
              name: name?.trim(),
              description: description?.trim(),
              url: url?.trim()
            })"
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
              class="input w-full"
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
              class="input w-full"
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
            <form
              method="dialog"
              @submit="resetForm"
            >
              <button
                :disabled="loading"
                class="btn btn-soft"
              >
                Cancel
              </button>
            </form>
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
        </template>
      </div>
    </dialog>
  </Teleport>
</template>

<script setup>
import { reactive, ref, toRef, toValue, onBeforeMount } from 'vue';
import { PlusCircleIcon } from '@heroicons/vue/24/outline';
import { useForm } from 'vee-validate';
import * as yup from 'yup';
import emitter from "../utilities/emitter.js";

const wishlistId = ref(null);
const editItemId = ref(null);

onBeforeMount(() => {
  emitter.on('show-add-item-modal', async (event) => {
    initializing.value = true;
    wishlistId.value = event.wishlistId;
    editItemId.value = event.editItemId ?? null;
    if (editItemId.value) {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/items/${editItemId.value}`)
        const data = await res.json()
        
        name.value = data.name;
        description.value = data.description;
        url.value = data.url;
      } catch (err) {
        console.error(err)
      }
    }
    addItemModal.value?.showModal();
    initializing.value = false;
  })
})

const initializing = ref(false);
const loading = ref(false);

const addItemModal = ref(null);

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

const onSubmit = async ({ name, description, url }) => {
  try {
    loading.value = true;

    const body = { name, description, url };

    if (!editItemId.value) body.added_by_id = 2;

    const res = await fetch(`${import.meta.env.VITE_API_URL}/${!editItemId.value ? `wishlists/${wishlistId.value}/item` : `items/${editItemId.value}` }`, {
      method: !editItemId.value ? 'POST' : 'PUT',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json()
    emitter.emit('add-item-modal-success', { action: !editItemId.value ? 'add' : 'edit', data })
    addItemModal.value?.close();
  } catch (err) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  name.value = '';
  description.value = '';
  url.value = '';
}
</script>