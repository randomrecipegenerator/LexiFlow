let leadId = null;

async function startChat() {
    const response = await apiFetch(`/chat/start`, { method: 'POST' });
    const data = await response.json();
    leadId = data.lead_id;
}
async function sendMessage() {
    const input = document.getElementById('user-input');
    const content = input.value;
    if (!content) return;
    appendMessage('user', content);
    input.value = '';
    const formData = new FormData();
    formData.append('content', content);
    const response = await apiFetch(`/chat/message?lead_id=${leadId}`, {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    appendMessage('ai', data.content);
}
async function uploadFile() {
    const fileInput = document.getElementById('file-input');
    if (fileInput.files.length === 0) return;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    const response = await apiFetch(`/chat/upload?lead_id=${leadId}`, {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    alert(`File ${data.filename} uploaded successfully!`);
}
async function completeChat() {
    const response = await apiFetch(`/chat/complete?lead_id=${leadId}`, { method: 'POST' });
    const data = await response.json();
    alert(`Intake complete! Status: ${data.status}, Score: ${data.score}`);
}
function appendMessage(role, content) {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.className = role === 'user' ? 'user-msg' : 'ai-msg';
    div.innerText = content;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}
document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('upload-btn').addEventListener('click', uploadFile);
document.getElementById('complete-btn').addEventListener('click', completeChat);
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
startChat();
