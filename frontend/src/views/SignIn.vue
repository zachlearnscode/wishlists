<template>
  <div class="p-3 flex justify-center">
    <div id="firebaseui-auth-container" class="w-full"></div>
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { auth } from "../../firebase.js"
import { EmailAuthProvider } from 'firebase/auth'
import { useAuthStore } from "../stores/auth"
import api from "../api/axios"
import * as firebaseui from 'firebaseui'
import 'firebaseui/dist/firebaseui.css'

const store = useAuthStore()

var uiConfig = {
  callbacks: {
    signInSuccessWithAuthResult: async function (authResult, redirectUrl) {
      const inviteId = sessionStorage.getItem("pendingInviteCode");
      const wishlistId = sessionStorage.getItem("pendingWishlistId");

      if (inviteId && wishlistId) {
        
        await api.post(`/wishlists/${wishlistId}/users`)
        window.location.href = `/wishlist/${wishlistId}`;
        sessionStorage.removeItem("pendingInviteCode");
        sessionStorage.removeItem("pendingWishlistId");
      } else window.location.href = '/dashboard';

      return false;
    },
  },
  signInOptions: [
    // firebase.auth.GoogleAuthProvider.PROVIDER_ID,
    // firebase.auth.FacebookAuthProvider.PROVIDER_ID,
    // firebase.auth.TwitterAuthProvider.PROVIDER_ID,
    // firebase.auth.GithubAuthProvider.PROVIDER_ID,
    EmailAuthProvider.PROVIDER_ID,
    // firebase.auth.PhoneAuthProvider.PROVIDER_ID,
    // firebaseui.auth.AnonymousAuthProvider.PROVIDER_ID
  ],
  tosUrl: '<your-tos-url>',
  privacyPolicyUrl: function() {
    window.location.assign('<your-privacy-policy-url>');
  }
};

var ui = firebaseui.auth.AuthUI.getInstance() || new firebaseui.auth.AuthUI(auth);
onMounted(() => ui.start('#firebaseui-auth-container', uiConfig))
</script>