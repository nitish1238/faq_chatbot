// Plain JavaScript (no frameworks) for the chat page.
// It talks to the Django API using fetch() and updates the page
// without ever reloading it.

// Django's CSRF token is put on the page by {% csrf_token %} in chat.html.
// We read it here so every POST request we send passes CSRF protection.
function getCsrfToken() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : "";
}

const messagesBox = document.getElementById("messages");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const errorBox = document.getElementById("error-box");
const newChatBtn = document.getElementById("new-chat-btn");
const conversationList = document.getElementById("conversation-list");

let currentConversationId = null;

// ---------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------

function showError(text) {
    errorBox.textContent = text;
    errorBox.hidden = false;
}

function clearError() {
    errorBox.hidden = true;
    errorBox.textContent = "";
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function appendMessage(message) {
    const div = document.createElement("div");
    div.className = "message " + (message.sender === "USER" ? "user" : "bot");

    const textNode = document.createElement("span");
    textNode.textContent = message.content;

    const timeNode = document.createElement("span");
    timeNode.className = "time";
    timeNode.textContent = formatTime(message.created_at);

    div.appendChild(textNode);
    div.appendChild(timeNode);
    messagesBox.appendChild(div);
    messagesBox.scrollTop = messagesBox.scrollHeight;
}

function setChatEnabled(enabled) {
    messageInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
}

function markActiveConversation(conversationId) {
    document.querySelectorAll(".conversation-item").forEach((item) => {
        item.classList.toggle("active", item.dataset.id === conversationId);
    });
}

// ---------------------------------------------------------------------
// Loading an existing conversation
// ---------------------------------------------------------------------

async function openConversation(conversationId) {
    clearError();
    currentConversationId = conversationId;
    markActiveConversation(conversationId);
    messagesBox.innerHTML = "";

    try {
        const response = await fetch(`/api/conversations/${conversationId}/`);
        if (!response.ok) {
            throw new Error("Could not load this conversation.");
        }
        const data = await response.json();
        data.messages.forEach(appendMessage);
        setChatEnabled(true);
    } catch (err) {
        showError(err.message || "Something went wrong while loading the chat.");
        setChatEnabled(false);
    }
}

// ---------------------------------------------------------------------
// Creating a new conversation
// ---------------------------------------------------------------------

async function createConversation() {
    clearError();
    try {
        const response = await fetch("/api/conversations/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
        });
        if (!response.ok) {
            throw new Error("Could not start a new chat.");
        }
        const conversation = await response.json();

        // Add it to the sidebar list.
        const li = document.createElement("li");
        li.className = "conversation-item active";
        li.dataset.id = conversation.id;
        li.textContent = conversation.title;
        li.addEventListener("click", () => openConversation(conversation.id));

        // Remove the "no chats yet" hint if it's there.
        const emptyHint = conversationList.querySelector(".empty-hint");
        if (emptyHint) emptyHint.remove();

        conversationList.prepend(li);
        markActiveConversation(conversation.id);

        currentConversationId = conversation.id;
        messagesBox.innerHTML = "";
        setChatEnabled(true);
        messageInput.focus();
    } catch (err) {
        showError(err.message || "Something went wrong while creating the chat.");
    }
}

// ---------------------------------------------------------------------
// Sending a message
// ---------------------------------------------------------------------

async function sendMessage(text) {
    clearError();
    setChatEnabled(false); // disable the send button while we wait for the reply

    try {
        const response = await fetch(`/api/conversations/${currentConversationId}/messages/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({ content: text }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "The server could not process your message.");
        }

        appendMessage(data.user_message);
        appendMessage(data.bot_message);

        // Update the conversation title in the sidebar in case this was
        // the first message (server sets the title from it).
        const listItem = conversationList.querySelector(`[data-id="${currentConversationId}"]`);
        if (listItem && listItem.textContent === "New chat") {
            listItem.textContent = data.user_message.content.slice(0, 50);
        }
    } catch (err) {
        showError(err.message || "Network error. Please try again.");
    } finally {
        setChatEnabled(true);
        messageInput.focus();
    }
}

// ---------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------

newChatBtn.addEventListener("click", createConversation);

document.querySelectorAll(".conversation-item[data-id]").forEach((item) => {
    item.addEventListener("click", () => openConversation(item.dataset.id));
});

messageForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const text = messageInput.value.trim();

    if (!text) {
        showError("Please type a message before sending.");
        return;
    }
    if (text.length > 500) {
        showError("Your message is too long (max 500 characters).");
        return;
    }
    if (!currentConversationId) {
        showError("Please start a new chat first.");
        return;
    }

    messageInput.value = "";
    sendMessage(text);
});

// If the user already has conversations, open the most recent one automatically.
const firstConversation = document.querySelector(".conversation-item[data-id]");
if (firstConversation) {
    openConversation(firstConversation.dataset.id);
}
