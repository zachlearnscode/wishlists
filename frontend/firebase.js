import { initializeApp } from 'firebase/app'
import { getAuth, connectAuthEmulator } from 'firebase/auth'

const firebaseConfig = {
  apiKey: "AIzaSyARQqqslNMTiWaLY9P92lxWshmep3HJ044",
  authDomain: "wishlists-64db1.firebaseapp.com",
  projectId: "wishlists-64db1",
  storageBucket: "wishlists-64db1.firebasestorage.app",
  messagingSenderId: "741461075978",
  appId: "1:741461075978:web:7e96d9514956b7fd0017f3"
};

const firebaseApp = initializeApp(firebaseConfig)
const auth = getAuth(firebaseApp)
connectAuthEmulator(auth, "http://127.0.0.1:9099")

export { firebaseApp, auth }