const chatDiv = document.getElementById("chat");
const userInput = document.getElementById("userInput");
const langSelect = document.getElementById("langSelect");

function appendMessage(message, type) {
  const msgDiv = document.createElement("div");
  msgDiv.className = type;
  msgDiv.textContent = message;
  chatDiv.appendChild(msgDiv);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

function sendMessage() {
  const message = userInput.value.trim();
  const lang = langSelect.value;

  if (!message) return;

  appendMessage("You: " + message, "user");
  userInput.value = "";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message, lang: lang }),
  })
    .then((response) => response.json())
    .then((data) => appendMessage("Bot: " + data.reply, "bot"))
    .catch((err) => appendMessage("Bot: Error occurred", "bot"));
}
