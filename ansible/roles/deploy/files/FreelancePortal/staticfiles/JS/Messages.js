document.addEventListener("DOMContentLoaded", function () {
    const contactId = new URLSearchParams(window.location.search).get("contact_id");
    const chatMessages = document.getElementById("chat-messages");
    let lastMessageIds = new Set();
    let tempIdCounter = -1;
    let intervalId = null;
    let isLoading = false;
    let chatIsOpen = localStorage.getItem('chatIsOpen') === 'true' || false;

    const updateChatOpenState = (isOpen) => {
        chatIsOpen = isOpen;
        localStorage.setItem('chatIsOpen', isOpen);
    };

    if (contactId) {
        if (window.innerWidth < 580) {
            const chatList = document.querySelector(".chat-list");
            const chatDisplay = document.querySelector(".chat-display");
    
            if (chatIsOpen) {
                if (chatList && chatDisplay) {
                    chatList.style.display = "none";
                    chatDisplay.style.display = "flex";
                }
            } else {
                if (chatList && chatDisplay) {
                    chatList.style.display = "block";
                    chatDisplay.style.display = "none";
                }
            }
        }
    
        loadMessages(contactId);
        setInterval(() => loadMessages(contactId), 1000);
    }

    if (window.innerWidth < 580) {
        const chatItems = document.querySelectorAll(".chat-item");
        chatItems.forEach(item => {
            if (!item.dataset.listenerAdded) {
                item.addEventListener("click", function () {
                    const chatList = document.querySelector(".chat-list");
                    const chatDisplay = document.querySelector(".chat-display");
                    
                    if (chatList && chatDisplay) {
                        chatList.style.display = "none";
                        chatDisplay.style.display = "flex";
                        updateChatOpenState(true);
                    } else {
                        console.error("Chat list or display elements not found");
                    }
                });
                item.dataset.listenerAdded = "true";
            }
        });
    }
        
    const sendBtn = document.getElementById("send-btn");
    if (sendBtn) {
        sendBtn.addEventListener("click", function () {
            const inputField = document.getElementById("chat-input");
            const message = inputField.value.trim();

            if (!message || !contactId || message.length > 500) {
                alert("Message must be between 1–500 characters.");
                return;
            }

            const tempId = tempIdCounter--;
            appendMessage(message, "outgoing", tempId, "Now", false);
            inputField.value = "";
            sendToServer(message, tempId);
        });
    }

    const chatInput = document.getElementById("chat-input");
    if (chatInput) {
        chatInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                sendBtn.click();
            }
        });
    }

    const closeBtn = document.getElementById("close-chat");
    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            const chatDisplay = document.querySelector(".chat-display");
            const chatList = document.querySelector(".chat-list");
            
            if (chatDisplay) {
                chatDisplay.style.visibility = "hidden";
                if (window.innerWidth < 580) {
                    chatDisplay.style.display = "none";
                    if (chatList) {
                        chatList.style.display = "block";
                    }
                    updateChatOpenState(false);
                }
            }

            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
        });
    }

    function appendMessage(text, type, messageId, timestamp, isRead) {
        if (lastMessageIds.has(messageId)) return;

        const wrapper = document.createElement("div");
        wrapper.className = type + "-chat chat-bubble";
        wrapper.dataset.messageId = messageId;

        const msg = document.createElement("p");
        msg.textContent = text;
        msg.className = "chat-text";

        const meta = document.createElement("small");
        meta.textContent = `${timestamp}${type === 'outgoing' ? (isRead ? ' • Read' : ' • Sent') : ''}`;
        meta.className = "chat-meta";

        wrapper.appendChild(msg);
        wrapper.appendChild(meta);
        chatMessages.insertBefore(wrapper, chatMessages.firstChild);

        lastMessageIds.add(messageId);
    }

    async function sendToServer(message, tempId) {
        try {
            const response = await fetch("/api/send-message/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ contact_id: contactId, message: message })
            });

            const result = await response.json();
            if (response.ok) {
                lastMessageIds.delete(tempId);
                lastMessageIds.add(result.message.id);

                const tempElem = chatMessages.querySelector(`[data-message-id="${tempId}"]`);
                if (tempElem) {
                    tempElem.dataset.messageId = result.message.id;
                    tempElem.querySelector("small").textContent = `${result.message.timestamp} • Sent`;
                }
            } else {
                showErrorAndRemove(tempId, result.error || "Send failed.");
            }
        } catch (err) {
            showErrorAndRemove(tempId, "Network error. Message not sent.");
        }
    }

    function showErrorAndRemove(tempId, errorText) {
        const tempElem = chatMessages.querySelector(`[data-message-id="${tempId}"]`);
        if (tempElem) {
            chatMessages.removeChild(tempElem);
            lastMessageIds.delete(tempId);
        }
        alert(errorText);
    }

    async function loadMessages(contactId) {
        if (isLoading) return;

        isLoading = true;
        try {
            const response = await fetch(`/api/get-messages/?contact_id=${contactId}`);
            const result = await response.json();

            if (!response.ok || !result.messages) return;

            const userName = document.getElementById("user-name");
            if (userName) userName.textContent = result.receiver_name;

            const chatDisplay = document.querySelector(".chat-display");
            if (chatDisplay) chatDisplay.style.visibility = "visible";

            for (const msg of result.messages) {
                if (!lastMessageIds.has(msg.id)) {
                    appendMessage(msg.content, msg.type, msg.id, msg.timestamp, msg.is_read);
                }
            }
        } catch (err) {
            console.error("Error loading messages:", err);
        } finally {
            isLoading = false;
        }
    }

    function getCookie(name) {
        try {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    const trimmed = cookie.trim();
                    if (trimmed.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        } catch (e) {
            console.error("Error getting cookie:", e);
            return null;
        }
    }
});
