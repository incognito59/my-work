import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js';
import { getAuth, GoogleAuthProvider } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "redcart-d792b.firebaseapp.com",
  projectId: "redcart-d792b",
  storageBucket: "redcart-d792b.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};

// Fill these values from the Firebase Console:
// 1) Open Project Settings > Your apps > Web app > Config
// 2) Copy apiKey, authDomain, projectId, storageBucket, messagingSenderId, appId
// 3) For Firebase Hosting or app setup, keep projectId as redcart-d792b
// 4) If using Firebase Auth or Google Sign-In, also enable Google provider in Authentication > Sign-in method

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export const DEMO_MODE = false;
export { auth, googleProvider, firebaseConfig };