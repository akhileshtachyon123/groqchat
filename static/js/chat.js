// =============================================
// GroqChat — Frontend Logic
// =============================================

const chatWindow  = document.getElementById("chatWindow");
const userInput   = document.getElementById("userInput");
const sendBtn     = document.getElementById("sendBtn");
const clearBtn    = document.getElementById("clearBtn");
const tokenCount  = document.getElementById("tokenCount");
const modelLabel  = document.getElementById("modelLabel");

let totalTokens = 0;
let isLoading   = false;

// ── Auto-resize textarea ──────────────────────
userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 160) + "px";
});

// ── Enter to send, Shift+Enter for newline ────
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

sendBtn.addEventListener("click", sendMessage);
clearBtn.addEventListener("click", clearChat);

// ── Starter chip handler ──────────────────────
function useStarter(btn) {
  userInput.value = btn.textContent;
  userInput.dispatchEvent(new Event("input"));
  sendMessage();
}

// ── Core send function ────────────────────────
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || isLoading) return;

  // Remove welcome state
  const welcome = document.getElementById("welcomeState");
  if (welcome) welcome.remove();

  // Render user bubble
  appendBubble("user", text);
  userInput.value = "";
  userInput.style.height = "auto";

  // Show typing indicator
  const typingEl = appendTyping();
  setLoading(true);

  try {
    const res  = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    typingEl.remove();

    if (data.error) {
      appendBubble("ai", `⚠️ ${data.error}`, true);
    } else {
      appendBubble("ai", data.reply);
      // Update token counter
      totalTokens += data.tokens_used || 0;
      tokenCount.textContent = totalTokens.toLocaleString();
      if (data.model) modelLabel.textContent = data.model;
    }
  } catch (err) {
    typingEl.remove();
    appendBubble("ai", "⚠️ Network error — is the server running?", true);
  }

  setLoading(false);
  scrollToBottom();
}

// ── Append a chat bubble ──────────────────────
function appendBubble(role, text, isError = false) {
  const row = document.createElement("div");
  row.className = "message-row";

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role}`;
  avatar.textContent = role === "user" ? "🧑" : "⚡";

  const bubble = document.createElement("div");
  bubble.className = `bubble ${isError ? "error" : role}`;
  bubble.innerHTML = role === "ai" ? renderMarkdown(text) : escapeHtml(text);

  if (role === "user") {
    row.appendChild(avatar);
    row.appendChild(bubble);
  } else {
    row.appendChild(avatar);
    row.appendChild(bubble);
  }

  chatWindow.appendChild(row);
  scrollToBottom();
  return row;
}

// ── Typing indicator ──────────────────────────
function appendTyping() {
  const row = document.createElement("div");
  row.className = "message-row";

  const avatar = document.createElement("div");
  avatar.className = "avatar ai";
  avatar.textContent = "⚡";

  const bubble = document.createElement("div");
  bubble.className = "bubble ai";
  bubble.innerHTML = `<span class="typing-indicator"><span></span><span></span><span></span></span>`;

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatWindow.appendChild(row);
  scrollToBottom();
  return row;
}

// ── Clear conversation ────────────────────────
async function clearChat() {
  await fetch("/clear", { method: "POST" });
  chatWindow.innerHTML = `
    <div class="welcome-state" id="welcomeState">
      <div class="welcome-icon">⚡</div>
      <h1>How can I help you today?</h1>
      <p>Ask me anything — I'm running on Groq's blazing-fast inference.</p>
      <div class="starter-chips">
        <button class="chip" onclick="useStarter(this)">Explain quantum computing simply</button>
        <button class="chip" onclick="useStarter(this)">Write a Python function to sort a dict</button>
        <button class="chip" onclick="useStarter(this)">What's the difference between REST and GraphQL?</button>
        <button class="chip" onclick="useStarter(this)">Give me 5 productivity tips for developers</button>
      </div>
    </div>`;
  totalTokens = 0;
  tokenCount.textContent = "0";
}

// ── Helpers ───────────────────────────────────
function setLoading(state) {
  isLoading = state;
  sendBtn.disabled = state;
  userInput.disabled = state;
}

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>");
}

// Minimal markdown renderer (bold, italic, code blocks, inline code, lists)
function renderMarkdown(text) {
  let html = escapeHtml(text)
    // Code blocks
    .replace(/```[\w]*\n?([\s\S]*?)```/g, (_, code) =>
      `<pre><code>${code.trim()}</code></pre>`)
    // Inline code
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    // Bold
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    // Italic
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // Unordered list items
    .replace(/^[-•]\s+(.+)$/gm, "<li>$1</li>")
    // Ordered list items
    .replace(/^\d+\.\s+(.+)$/gm, "<li>$1</li>")
    // Wrap consecutive <li> in <ul>
    .replace(/(<li>[\s\S]*?<\/li>)+/g, m => `<ul>${m}</ul>`)
    // Paragraphs (double newline)
    .replace(/\n\n/g, "</p><p>")
    // Single newlines
    .replace(/\n/g, "<br>");

  return `<p>${html}</p>`;
}
