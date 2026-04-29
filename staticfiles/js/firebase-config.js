import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js';
import { getAuth, GoogleAuthProvider } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js';

const firebaseConfig = {
  apiKey: "AIzaSyDrJYsqt6s0l9XxFuxzK4k340AoumMu4Fg",
  authDomain: "redcart-d792b.firebaseapp.com",
  projectId: "redcart-d792b",
  storageBucket: "redcart-d792b.firebasestorage.app",
  messagingSenderId: "803296445904",
  appId: "1:803296445904:web:ad07772f2c7ee7148fa5d5"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export const DEMO_MODE = false;
export { auth, googleProvider, firebaseConfig };