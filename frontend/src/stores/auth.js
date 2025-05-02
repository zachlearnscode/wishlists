import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../../firebase.js'
import { onAuthStateChanged, signOut as firebaseSignOut } from 'firebase/auth'
import api from '../api/axios.js'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();

  const loading = ref(true)
  const wishlistsUser = ref(null)
  const isAuthenticated = ref(false)

  onAuthStateChanged(auth, async (user) => {
      try {
        if (user) {
          const res = await api('/user');
          wishlistsUser.value = res.data;
        } else wishlistsUser.value = null;
      } catch (err) {
        console.error(err);
        wishlistsUser.value = null;
        router.push("/sign-in");
      } finally {
        isAuthenticated.value = !!user
        loading.value = false
      }
  })

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