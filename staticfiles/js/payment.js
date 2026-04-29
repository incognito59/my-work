// Paystack inline integration helper
// DEMO KEY - Replace with your test key from: https://dashboard.paystack.com
const PAYSTACK_PUBLIC_KEY = 'pk_test_51a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p';

function $(s){return document.querySelector(s)}
function show(el, cls, text){
  el.innerHTML = `<div class="message ${cls}">${text}</div>`;
}

export function initPayment(){
  const form = $('#payment-form');
  const msg = $('#payment-msg');
  const emailInput = $('#pay-email');
  const amountInput = $('#pay-amount');

  // populate email if user logged in
  try{
    const user = JSON.parse(localStorage.getItem('user')||'null');
    if(user && user.email) emailInput.value = user.email;
  }catch(e){}

  form.addEventListener('submit', function(e){
    e.preventDefault();
    show(msg,'','');
    const email = emailInput.value.trim();
    const amount = parseFloat(amountInput.value) || 0;
    if(!email || amount<=0){
      show(msg,'error','Please provide a valid email and amount');
      return;
    }

    // initialize Paystack
    const handler = PaystackPop.setup({
      key: PAYSTACK_PUBLIC_KEY,
      email: email,
      amount: Math.round(amount*100), // in kobo
      currency: 'NGN',
      channels: ['card', 'bank', 'ussd'],
      callback: function(response){
        show(msg,'success',`Payment successful. Reference: ${response.reference}`);
        console.log('PAYSTACK success', response);
      },
      onClose: function(){
        show(msg,'error','Payment popup closed or cancelled');
      }
    });
    handler.openIframe();
  });
}
