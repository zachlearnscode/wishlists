<template>
  <section class="min-h-[calc(100vh-53px)] bg-gradient-to-br from-indigo-100 to-white text-gray-800">
    <div class="max-w-4xl mx-auto px-6 py-20 text-center">
      <h1 class="text-4xl sm:text-5xl font-bold mb-6 leading-tight">
        Build & Share Beautiful Wishlists
      </h1>
      <p class="text-lg sm:text-xl text-gray-600 mb-8">
        Create collaborative gift lists with friends and family — privately or together.
      </p>
      <div class="flex flex-col sm:flex-row justify-center gap-4 mb-16">
        <RouterLink to="/sign-in" class="btn btn-primary btn-wide text-white text-lg">
          Get Started
        </RouterLink>
        <RouterLink to="/sign-in" class="btn btn-soft btn-wide text-lg">
          Sign In
        </RouterLink>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-8 text-left text-sm sm:text-base">
        <div class="bg-white shadow rounded-2xl p-6">
          <h3 class="font-semibold text-indigo-600 mb-2">✨ Simple & Clean</h3>
          <p>Easily create wishlists for birthdays, holidays, or group events.</p>
        </div>
        <div class="bg-white shadow rounded-2xl p-6">
          <h3 class="font-semibold text-indigo-600 mb-2">🔒 Private & Secure</h3>
          <p>Only invited users can view or contribute to your lists.</p>
        </div>
        <div class="bg-white shadow rounded-2xl p-6">
          <h3 class="font-semibold text-indigo-600 mb-2">🤝 Collaborative</h3>
          <p>Friends can claim gifts, add ideas, and mark items as acquired.</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// No logic needed for now
</script>
