import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword,
         signInWithPopup, GoogleAuthProvider, FacebookAuthProvider,
         GithubAuthProvider, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js';
import { auth } from './firebase-config.js';

// Utilities
function $(sel) { return document.querySelector(sel) }
function showMessage(el, type, text) {
  if (el) el.innerHTML = `<div class="message ${type}">${text}</div>`;
}
function setLoading(form, on = true) {
  if (form) on ? form.classList.add('loading') : form.classList.remove('loading');
}

// Get Django CSRF token from cookie
function getCookie(name) {
  const val = document.cookie.split('; ').find(r => r.startsWith(name + '='));
  return val ? val.split('=')[1] : '';
}

// Send Firebase ID token to Django backend
async function syncWithBackend(user) {
  try {
    const idToken = await user.getIdToken();
    const res = await fetch('/auth/google/callback/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token: idToken })
    });

    const data = await res.json();

    if (data.success) {
      localStorage.setItem('user', JSON.stringify({
        email: user.email,
        name: user.displayName || user.email
      }));
      window.location.href = data.redirect || '/products/';
    } else {
      console.error('Backend error:', data.error);
      alert('Login failed: ' + data.error);
    }
  } catch (err) {
    console.error('Backend sync error:', err.message);
    alert('Connection error. Please try again.');
  }
}

// Social sign-in helper
async function socialSignIn(provider) {
  console.log('Signing in with:', provider.providerId);
  try {
    const result = await signInWithPopup(auth, provider);
    await syncWithBackend(result.user);
  } catch (err) {
    console.error('Sign-in error:', err.code, err.message);
    if (err.code === 'auth/popup-closed-by-user') {
      console.log('Popup closed by user.');
      return;
    }
    if (err.code === 'auth/popup-blocked') {
      alert('Popup was blocked by your browser. Please allow popups for this site.');
      return;
    }
    alert('Sign-in failed: ' + err.message);
  }
}

// Login flow
export async function initLogin() {
  const form = $('#login-form');
  const msg = $('#login-msg');

  $('#btn-google')?.addEventListener('click', () => socialSignIn(new GoogleAuthProvider()));
  $('#btn-facebook')?.addEventListener('click', () => socialSignIn(new FacebookAuthProvider()));
  $('#btn-github')?.addEventListener('click', () => socialSignIn(new GithubAuthProvider()));

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showMessage(msg, '', '');
    setLoading(form, true);
    const email = $('#login-email').value.trim();
    const password = $('#login-password').value.trim();
    try {
      if (!email || !password) throw new Error('Email and password required');
      const res = await signInWithEmailAndPassword(auth, email, password);
      await syncWithBackend(res.user);
    } catch (err) {
      showMessage(msg, 'error', err.message);
    } finally {
      setLoading(form, false);
    }
  });
}

// Register flow
export async function initRegister() {
  const form = $('#register-form');
  const msg = $('#register-msg');

  $('#reg-google')?.addEventListener('click', () => socialSignIn(new GoogleAuthProvider()));
  $('#reg-facebook')?.addEventListener('click', () => socialSignIn(new FacebookAuthProvider()));
  $('#reg-github')?.addEventListener('click', () => socialSignIn(new GithubAuthProvider()));

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showMessage(msg, '', '');
    setLoading(form, true);
    const name = $('#reg-name').value.trim();
    const email = $('#reg-email').value.trim();
    const password = $('#reg-password').value.trim();
    try {
      if (!name || !email || !password) throw new Error('All fields required');
      if (password.length < 6) throw new Error('Password must be 6+ characters');
      const res = await createUserWithEmailAndPassword(auth, email, password);
      await syncWithBackend(res.user);
    } catch (err) {
      showMessage(msg, 'error', err.message);
    } finally {
      setLoading(form, false);
    }
  });
}

// Observe auth state
export function observeAuth() {
  onAuthStateChanged(auth, user => {
    if (user) {
      localStorage.setItem('user', JSON.stringify({
        email: user.email,
        name: user.displayName || user.email
      }));
    } else {
      localStorage.removeItem('user');
    }
  });
}