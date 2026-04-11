// Firebase configuration
// IMPORTANT: Replace with your real Firebase config from https://console.firebase.google.com
// Get config: Project Settings → Your Apps → Web → Copy config
const firebaseConfig = {
  apiKey: "AIzaSyAwGuVeLd3qQ7nX8Y-2K9R3n9SPnX8Y-9Qg",
  authDomain: "retail-auth-demo.firebaseapp.com",
  projectId: "retail-auth-demo",
  storageBucket: "retail-auth-demo.appspot.com",
  messagingSenderId: "246802468024",
  appId: "1:246802468024:web:abc123def456abc123def4"
};

// DEMO MODE: If real Firebase isn't configured, use this for testing
export const DEMO_MODE = true;

// Export for auth.js
export { firebaseConfig };
