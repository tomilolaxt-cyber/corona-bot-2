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

// Creators Modal Functions
function showCreators() {
    const modal = document.getElementById('creatorsModal');
    modal.style.display = 'block';
}

function closeCreators() {
    const modal = document.getElementById('creatorsModal');
    modal.style.display = 'none';
}

// Install Modal Functions
function showInstallInstructions() {
    console.log('Install button clicked!'); // Debug log
    const modal = document.getElementById('installModal');
    
    if (!modal) {
        alert('Install modal not found! Please refresh the page.');
        return;
    }
    
    modal.style.display = 'block';
    
    // Detect device and show appropriate instructions
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isAndroid = /Android/.test(navigator.userAgent);
    
    const iosInstructions = document.getElementById('iosInstructions');
    const androidInstructions = document.getElementById('androidInstructions');
    
    if (isIOS) {
        if (iosInstructions) iosInstructions.style.display = 'block';
        if (androidInstructions) androidInstructions.style.display = 'none';
    } else if (isAndroid) {
        if (androidInstructions) androidInstructions.style.display = 'block';
        if (iosInstructions) iosInstructions.style.display = 'none';
    } else {
        // Show both for desktop
        if (androidInstructions) androidInstructions.style.display = 'block';
        if (iosInstructions) iosInstructions.style.display = 'block';
    }
}

function closeInstallModal() {
    const modal = document.getElementById('installModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    const creatorsModal = document.getElementById('creatorsModal');
    const installModal = document.getElementById('installModal');
    if (event.target == creatorsModal) {
        creatorsModal.style.display = 'none';
    }
    if (event.target == installModal) {
        installModal.style.display = 'none';
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeCreators();
        closeInstallModal();
    }
});
