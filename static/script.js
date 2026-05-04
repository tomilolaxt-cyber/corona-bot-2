// Chat functionality
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatMessages = document.getElementById('chatMessages');
const sendBtn = document.querySelector('.send-btn');
const loading = document.getElementById('loading');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    
    if (message) {
        addMessage(message, 'user');
        userInput.value = '';
        sendBtn.disabled = true;
        loading.style.display = 'block';
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                addMessage(data.response, 'bot');
            } else {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, I encountered a connection error. Please try again.', 'bot');
        } finally {
            sendBtn.disabled = false;
            loading.style.display = 'none';
            userInput.focus();
        }
    }
});

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const p = document.createElement('p');
    p.textContent = text;
    
    contentDiv.appendChild(p);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function askQuestion(question) {
    userInput.value = question;
    chatForm.dispatchEvent(new Event('submit'));
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat?')) {
        fetch('/api/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => response.json())
          .then(data => {
              if (data.success) {
                  chatMessages.innerHTML = `
                      <div class="message bot-message">
                          <div class="message-content">
                              <p>Chat cleared! Hello! I'm Corona Bot, an AI assistant. What would you like to know about Corona Schools?</p>
                          </div>
                      </div>
                  `;
                  userInput.focus();
              }
          })
          .catch(error => console.error('Error:', error));
    }
}

// Focus input on load
window.addEventListener('load', () => {
    userInput.focus();
});
