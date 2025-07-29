document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patient-chatbot-form');
    const input = document.getElementById('patient-chatbot-input');
    const messages = document.getElementById('patient-chatbot-messages');
  
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      const userMsg = input.value.trim();
      if (!userMsg) return;
      messages.innerHTML += `<div><b>You:</b> ${userMsg}</div>`;
      input.value = '';
      messages.innerHTML += `<div><i>Chatbot is typing...</i></div>`;
  
      try {
        const resp = await fetch('/patient_chatbot', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({query: userMsg})
        });
        const data = await resp.json();
        messages.innerHTML = messages.innerHTML.replace('<div><i>Chatbot is typing...</i></div>', '');
        if (data.response) {
          messages.innerHTML += `<div><b>Chatbot:</b> ${data.response.replace(/\\n/g, '<br>')}</div>`;
        } else if (data.error) {
          messages.innerHTML += `<div style="color:red;"><b>Error:</b> ${data.error}</div>`;
        }
      } catch (err) {
        messages.innerHTML += `<div style="color:red;"><b>Error:</b> Could not reach chatbot.</div>`;
      }
      messages.scrollTop = messages.scrollHeight;
    });
  });