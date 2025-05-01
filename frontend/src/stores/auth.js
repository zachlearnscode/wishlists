import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../../firebase.js'
import { onAuthStateChanged, signOut as firebaseSignOut } from 'firebase/auth'

export const useAuthStore = defineStore('auth', () => {
  const loading = ref(true)

  const wishlistsUser = ref(null)
  const isAuthenticated = ref(false)

  onAuthStateChanged(auth, async (user) => {

      try {
        if (user) {
          const { uid } = user;
          const res = await fetch(`${import.meta.env.VITE_API_URL}/users/firebase-uid/${uid}`);
          const data = await res.json();

          wishlistsUser.value = data;
        } else wishlistsUser.value = null;
      } catch (err) {
        console.error(err)
      } finally {
        isAuthenticated.value = !!user
        loading.value = false
      }
  })

  const router = useRouter();
  const signOut = async () => {
    await firebaseSignOut(auth)
    await router.push("/sign-in");
  }

  return {
    wishlistsUser,
    isAuthenticated,
    loading,
    signOut
  }
})