const apiBase = '/api/v1';

// ------------------------------
// Sidebar Tabs
// ------------------------------
document.querySelectorAll('.menu button').forEach(btn => {
  btn.addEventListener('click', e => {
    document.querySelectorAll('.menu button').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    const tab = e.target.getAttribute('data-tab');
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById(tab).classList.add('active');
  });
});

// ------------------------------
// Upload PDF
// ------------------------------
document.getElementById('upload_btn').addEventListener('click', async () => {
  const fileInput = document.getElementById('upload_file');
  if (!fileInput.files.length) return alert('Choose a PDF');
  const f = fileInput.files[0];
  const fd = new FormData();
  fd.append('file', f);
  const res = await fetch(`${apiBase}/uploadfile`, { method: 'POST', body: fd });
  const json = await res.json();
  document.getElementById('upload_result').innerText = JSON.stringify(json, null, 2);
});

// ------------------------------
// Retrieve File
// ------------------------------
document.getElementById('retrieve_btn').addEventListener('click', async () => {
  const id = document.getElementById('retrieve_id').value.trim();
  if (!id) return alert('Enter File ID');
  const res = await fetch(`${apiBase}/uploadfile/${id}`);
  const json = await res.json();
  document.getElementById('retrieve_result').innerText = JSON.stringify(json, null, 2);
});

// ------------------------------
// Update PDF
// ------------------------------
document.getElementById('update_btn').addEventListener('click', async () => {
  const id = document.getElementById('update_id').value.trim();
  const fileInput = document.getElementById('update_file');
  if (!id || !fileInput.files.length) return alert('Enter File ID and PDF');
  const f = fileInput.files[0];
  const fd = new FormData();
  fd.append('file', f);
  const res = await fetch(`${apiBase}/uploadfile/${id}`, { method: 'PUT', body: fd });
  const json = await res.json();
  document.getElementById('update_result').innerText = JSON.stringify(json, null, 2);
});

// ------------------------------
// Delete PDF
// ------------------------------
document.getElementById('delete_btn').addEventListener('click', async () => {
  const id = document.getElementById('delete_id').value.trim();
  if (!id) return alert('Enter File ID');
  const res = await fetch(`${apiBase}/uploadfile/${id}`, { method: 'DELETE' });
  const json = await res.json();
  document.getElementById('delete_result').innerText = JSON.stringify(json, null, 2);
});

// ------------------------------
// Chat System
// ------------------------------
document.getElementById('ask_btn').addEventListener('click', async () => {
  const id = document.getElementById('chat_id').value.trim();
  const q = document.getElementById('question').value.trim();
  if (!id || !q) return alert('Provide File ID and question');
  const chatBox = document.getElementById('chat_box');

  const userMsg = document.createElement('div');
  userMsg.className = 'chat-message chat-user';
  userMsg.textContent = q;
  chatBox.appendChild(userMsg);

  const botMsg = document.createElement('div');
  botMsg.className = 'chat-message chat-bot';
  botMsg.textContent = '🤖 thinking...';
  chatBox.appendChild(botMsg);
  chatBox.scrollTop = chatBox.scrollHeight;

  const res = await fetch(`${apiBase}/query_pdf/${encodeURIComponent(id)}?question=${encodeURIComponent(q)}`);
  const json = await res.json();

  botMsg.textContent = json.answer || "No answer found.";
  document.getElementById('question').value = '';
  chatBox.scrollTop = chatBox.scrollHeight;
});

// ------------------------------
// 🌗 Theme Toggle
// ------------------------------
const themeBtn = document.getElementById('theme_toggle');
const body = document.body;

// Load theme from localStorage
if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark');
  themeBtn.textContent = '☀️ Light Mode';
}

themeBtn.addEventListener('click', () => {
  body.classList.toggle('dark');
  const isDark = body.classList.contains('dark');
  themeBtn.textContent = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
});
