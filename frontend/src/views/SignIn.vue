<template>
  <div id="firebaseui-auth-container"></div>
</template>

<script setup>
import firebase from 'firebase/compat/app';
import * as firebaseui from 'firebaseui'
import 'firebaseui/dist/firebaseui.css'

const firebaseConfig = {
  apiKey: "AIzaSyARQqqslNMTiWaLY9P92lxWshmep3HJ044",
  authDomain: "wishlists-64db1.firebaseapp.com",
  projectId: "wishlists-64db1",
  storageBucket: "wishlists-64db1.firebasestorage.app",
  messagingSenderId: "741461075978",
  appId: "1:741461075978:web:7e96d9514956b7fd0017f3"
};

const app = firebase.initializeApp(firebaseConfig);

var uiConfig = {
  signInSuccessUrl: `${import.meta.env.VITE_APP_URL}/dashboard`,
  signInOptions: [
    // Leave the lines as is for the providers you want to offer your users.
    // firebase.auth.GoogleAuthProvider.PROVIDER_ID,
    // firebase.auth.FacebookAuthProvider.PROVIDER_ID,
    // firebase.auth.TwitterAuthProvider.PROVIDER_ID,
    // firebase.auth.GithubAuthProvider.PROVIDER_ID,
    firebase.auth.EmailAuthProvider.PROVIDER_ID,
    // firebase.auth.PhoneAuthProvider.PROVIDER_ID,
    // firebaseui.auth.AnonymousAuthProvider.PROVIDER_ID
  ],
  // tosUrl and privacyPolicyUrl accept either url string or a callback
  // function.
  // Terms of service url/callback.
  tosUrl: '<your-tos-url>',
  // Privacy policy url/callback.
  privacyPolicyUrl: function() {
    window.location.assign('<your-privacy-policy-url>');
  }
};

const auth = firebase.auth();
auth.useEmulator("http://127.0.0.1:9099");

// Initialize the FirebaseUI Widget using Firebase.
var ui = new firebaseui.auth.AuthUI(firebase.auth());
// The start method will wait until the DOM is loaded.
ui.start('#firebaseui-auth-container', uiConfig);
</script>