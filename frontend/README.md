# 🛒 RedCart Frontend - Complete Setup

A modern ecommerce authentication and payment system frontend with **Firebase Auth** (email + Google/Facebook/GitHub) and **Paystack Payment**.

## 📋 Files Included

- `index.html` - Login page with social auth buttons
- `register.html` - Registration page with social signup
- `payment.html` - Checkout page with Paystack payment
- `css/styles.css` - Responsive Amazon/Jumia-like styling
- `js/firebase-config.js` - Firebase configuration (update with your keys)
- `js/auth.js` - Firebase authentication flows
- `js/payment.js` - Paystack payment integration

## 🚀 Quick Start

### 1. Start Local Server
```bash
cd frontend
python -m http.server 8000
```
Then open: **http://localhost:8000**

### 2. Test Login
Try these demo credentials (or create new ones):
- Email: `test@example.com`
- Password: `test123456`

Or click **Google**, **Facebook**, or **GitHub** buttons (requires Firebase setup).

## ⚙️ Configuration

### Firebase Setup (Optional - For Social Login)
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project named "RedCart"
3. Enable Authentication:
   - Email/Password
   - Google OAuth
   - Facebook OAuth
   - GitHub OAuth
4. Copy your config from **Project Settings → Your Apps → Web**
5. Replace placeholders in `js/firebase-config.js`:
   ```javascript
   const firebaseConfig = {
     apiKey: "YOUR_KEY",
     authDomain: "YOUR_DOMAIN",
     projectId: "YOUR_PROJECT",
     storageBucket: "YOUR_STORAGE",
     messagingSenderId: "YOUR_SENDER",
     appId: "YOUR_APP"
   };
   ```

### Paystack Setup (For Payments)
1. Go to [Paystack Dashboard](https://dashboard.paystack.com)
2. Get your **Test Public Key** (starts with `pk_test_`)
3. Replace in `js/payment.js`:
   ```javascript
   const PAYSTACK_PUBLIC_KEY = 'pk_test_YOUR_KEY';
   ```

### Test Payment
Use these test card details:
- **Visa/Mastercard**: `4111 1111 1111 1111`
- **Exp**: Any future date (e.g., `12/25`)
- **CVV**: Any 3 digits (e.g., `123`)
- **Amount**: Any amount in ₦ (NGN)

## 🎨 Features

✅ **Complete Authentication**
- Email/Password login & registration
- Google OAuth login
- Facebook OAuth login
- GitHub OAuth login
- Auto-redirect to payment after auth

✅ **Payment Processing**
- Paystack inline payment popup
- Support for: Visa, Mastercard, Verve, Bank Transfer, USSD
- NGN currency (Nigerian Naira)
- Success/error message handling

✅ **Modern UI/UX**
- Amazon/Jumia-like responsive design
- Dark/Light theme ready
- Professional form styling
- Loading states
- Smooth transitions and hover effects

## 📱 Mobile Responsive
All pages are fully responsive and tested on mobile browsers.

## 🔒 Security
- Firebase handles auth token management
- Paystack handles PCI compliance
- HTTPS recommended for production

## 📞 Support
For Firebase issues: https://firebase.google.com/docs/auth
For Paystack issues: https://paystack.com/resources

---
**For your presentation tomorrow**: Just open `index.html` in browser and test the login/register/payment flow! 🎉
