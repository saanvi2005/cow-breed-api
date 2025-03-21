async function askQuestion() {
    const question = document.getElementById("question").value;
    const chatBox = document.getElementById("chat-box");

    if (!question) {
        alert("Please enter a question!");
        return;
    }

    const userMessage = document.createElement("div");
    userMessage.classList.add("chat-message", "user");
    userMessage.innerText = question;
    chatBox.appendChild(userMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    const botMessage = document.createElement("div");
    botMessage.classList.add("chat-message", "bot");
    botMessage.innerText = "Typing...";
    chatBox.appendChild(botMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("https://cow-breed-api.onrender.com/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question, language: "en" }) // Change language if needed
        });

        console.log("Response Status:", response.status);

        if (!response.ok) {
            throw new Error("Server responded with an error");
        }

        const data = await response.json();
        console.log("API Response:", data);

        botMessage.innerText = data.response || "I don't understand that.";
    } catch (error) {
        console.error("Error:", error);
        botMessage.innerText = "Error connecting to server.";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
    document.getElementById("question").value = "";
}

