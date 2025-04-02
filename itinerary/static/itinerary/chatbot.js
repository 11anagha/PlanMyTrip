// // document.addEventListener("DOMContentLoaded", function () {
// //     const chatIcon = document.getElementById("chatbot-icon");
// //     const chatPopup = document.getElementById("chat-popup");
// //     const closeChat = document.getElementById("close-chat");
// //     const sendBtn = document.getElementById("send-btn");
// //     const userInput = document.getElementById("user-input");
// //     const chatMessages = document.getElementById("chat-messages");

//     // Toggle chat popup
//     // chatIcon.addEventListener("click", function () {
//     //     chatPopup.style.display = (chatPopup.style.display === "block") ? "none" : "block";
//     // });

//     // Close chat popup
//     // closeChat.addEventListener("click", function () {
//     //     chatPopup.style.display = "none";
//     // });

//     // Send message when clicking "Send"
//     // sendBtn.addEventListener("click", function () {
//     //     sendMessage();
//     // });

//     // Send message when pressing "Enter"
//     // userInput.addEventListener("keypress", function (event) {
//     //     if (event.key === "Enter") {
//     //         sendMessage();
//     //     }
//     // });

//     function sendMessage() {
//         let message = userInput.value.trim();
//         if (!message) return;

//         // Display user message
//         chatMessages.innerHTML += `<div class="user-message">${message}</div>`;
//         chatMessages.scrollTop = chatMessages.scrollHeight;

//         // Send message to Django backend
//         fetch("/chatbot_response/", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/x-www-form-urlencoded",
//             },
//             body: new URLSearchParams({ message: message }),
//         })
//         .then(response => response.json())
//         .then(data => {
//             // Display chatbot response
//             chatMessages.innerHTML += `<div class="bot-message">${data.response || "No response"}</div>`;
//             chatMessages.scrollTop = chatMessages.scrollHeight;
//         })
//         .catch(error => {
//             console.error("Fetch error:", error);
//             chatMessages.innerHTML += `<div class="error-message">Error: Failed to connect</div>`;
//         });

//         // Clear input field
//         userInput.value = "";
//     }
// });
