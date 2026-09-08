// Paystack inline integration helper
const PAYSTACK_PUBLIC_KEY = window.PAYSTACK_PUBLIC_KEY || '';

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

    if (!PAYSTACK_PUBLIC_KEY || !window.PaystackPop || !window.PaystackPop.setup) {
      show(msg,'error','Online payments are temporarily unavailable');
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
