import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup, GoogleAuthProvider, FacebookAuthProvider, GithubAuthProvider, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js';
import { firebaseConfig, DEMO_MODE } from './firebase-config.js';

// Initialize Firebase
let app, auth;
try {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
  console.log('✓ Firebase initialized successfully');
} catch(e) {
  console.warn('Firebase init issue (demo mode enabled):', e.message);
}

// Utilities for UI
function $(sel){return document.querySelector(sel)}
function showMessage(el, type, text){
  el.innerHTML = `<div class="message ${type}">${text}</div>`;
}
function setLoading(form, on=true){
  if(on) form.classList.add('loading'); else form.classList.remove('loading');
}

// Demo sign-in (for testing without real Firebase)
async function demoSocialSignIn(provider) {
  const providerName = provider.providerId ? provider.providerId.split('.')[0] : 'provider';
  const email = `demo-${providerName}-${Date.now()}@redcart.com`;
  const displayName = providerName.charAt(0).toUpperCase() + providerName.slice(1);
  console.log('✓ Demo Sign-in:', {email, displayName});
  localStorage.setItem('user', JSON.stringify({email, name: `${displayName} User`, provider: providerName}));
  return {user: {email, displayName: `${displayName} User`}};
}

// Login flow
export async function initLogin(){
  const form = $('#login-form');
  const msg = $('#login-msg');
  const googleBtn = $('#btn-google');
  const fbBtn = $('#btn-facebook');
  const ghBtn = $('#btn-github');

  console.log('✓ Setting up login handlers...');
  
  if(googleBtn) {
    googleBtn.addEventListener('click', async ()=> {
      console.log('Google clicked');
      await socialSignIn(new GoogleAuthProvider());
    });
  }
  if(fbBtn) {
    fbBtn.addEventListener('click', async ()=> {
      console.log('Facebook clicked');
      await socialSignIn(new FacebookAuthProvider());
    });
  }
  if(ghBtn) {
    ghBtn.addEventListener('click', async ()=> {
      console.log('GitHub clicked');
      await socialSignIn(new GithubAuthProvider());
    });
  }

  if(form) {
    form.addEventListener('submit', async (e)=>{
      e.preventDefault();
      showMessage(msg,'','');
      setLoading(form,true);
      const email = $('#login-email').value.trim();
      const password = $('#login-password').value.trim();
      try{
        if (!email || !password) throw new Error('Email and password required');
        if (!auth) throw new Error('Firebase not initialized');
        const res = await signInWithEmailAndPassword(auth, email, password);
        showMessage(msg,'success','✓ Login successful — redirecting...');
        localStorage.setItem('user', JSON.stringify({email:res.user.email, name:res.user.displayName||res.user.email}));
        setTimeout(()=> location.href = 'payment.html',800);
      }catch(err){
        showMessage(msg,'error', err.message);
      }finally{setLoading(form,false)}
    });
  }
}

// Register flow
export async function initRegister(){
  const form = $('#register-form');
  const msg = $('#register-msg');
  const googleBtn = $('#reg-google');
  const fbBtn = $('#reg-facebook');
  const ghBtn = $('#reg-github');

  console.log('✓ Setting up register handlers...');

  if(googleBtn) {
    googleBtn.addEventListener('click', async ()=> {
      console.log('Reg: Google clicked');
      await socialSignIn(new GoogleAuthProvider());
    });
  }
  if(fbBtn) {
    fbBtn.addEventListener('click', async ()=> {
      console.log('Reg: Facebook clicked');
      await socialSignIn(new FacebookAuthProvider());
    });
  }
  if(ghBtn) {
    ghBtn.addEventListener('click', async ()=> {
      console.log('Reg: GitHub clicked');
      await socialSignIn(new GithubAuthProvider());
    });
  }

  if(form) {
    form.addEventListener('submit', async (e)=>{
      e.preventDefault();
      showMessage(msg,'','');
      setLoading(form,true);
      const name = $('#reg-name').value.trim();
      const email = $('#reg-email').value.trim();
      const password = $('#reg-password').value.trim();
      try{
        if (!name || !email || !password) throw new Error('All fields required');
        if (password.length < 6) throw new Error('Password must be 6+ characters');
        if (!auth) throw new Error('Firebase not initialized');
        const res = await createUserWithEmailAndPassword(auth, email, password);
        showMessage(msg,'success','✓ Account created — redirecting...');
        localStorage.setItem('user', JSON.stringify({email:res.user.email, name:name||res.user.email}));
        setTimeout(()=> location.href = 'payment.html',900);
      }catch(err){
        showMessage(msg,'error', err.message);
      }finally{setLoading(form,false)}
    });
  }
}

// Social sign-in helper
async function socialSignIn(provider){
  const pname = provider.providerId;
  console.log('↓ Attempting sign-in with:', pname);
  try{
    if (DEMO_MODE || !auth) {
      console.log('→ Using DEMO mode');
      const result = await demoSocialSignIn(provider);
      const user = result.user;
      localStorage.setItem('user', JSON.stringify({email:user.email, name:user.displayName||user.email}));
      setTimeout(()=> location.href = 'payment.html', 600);
      return;
    }
    
    console.log('→ Using real Firebase');
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    localStorage.setItem('user', JSON.stringify({email:user.email, name:user.displayName||user.email}));
    setTimeout(()=> location.href = 'payment.html', 600);
  }catch(err){
    console.error('✗ Error:', err.code, err.message);
    alert('Sign-in failed: ' + err.message);
  }
}

// Observe auth state
export function observeAuth(){
  if (!auth) return;
  onAuthStateChanged(auth, user => {
    if(user) localStorage.setItem('user', JSON.stringify({email:user.email, name:user.displayName||user.email}));
    else localStorage.removeItem('user');
  });
}
