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

// OTP Login Functions
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('otpMessage').textContent = '';
    setTimeout(() => document.getElementById('loginEmail').focus(), 100);
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function backToEmail() {
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('otpMessage').textContent = '';
}

async function sendOTP() {
    const email = document.getElementById('loginEmail').value.trim();
    const btn = document.querySelector('#step1 .otp-btn');
    const msg = document.getElementById('otpMessage');

    if (!email || !email.includes('@')) {
        msg.textContent = '❌ Please enter a valid email address';
        msg.className = 'otp-error';
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Sending...';
    msg.textContent = '';

    try {
        const res = await fetch('/api/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (data.success) {
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            document.getElementById('otpSentMsg').textContent = `✅ Code sent to ${email}! Check your inbox.`;
            setTimeout(() => document.getElementById('otpCode').focus(), 100);
        } else {
            msg.textContent = '❌ ' + data.error;
            msg.className = 'otp-error';
        }
    } catch (e) {
        msg.textContent = '❌ Connection error. Please try again.';
        msg.className = 'otp-error';
    }

    btn.disabled = false;
    btn.textContent = 'Send Code 📧';
}

async function verifyOTP() {
    const email = document.getElementById('loginEmail').value.trim();
    const code = document.getElementById('otpCode').value.trim();
    const btn = document.querySelector('#step2 .otp-btn');
    const msg = document.getElementById('otpMessage');

    if (!code || code.length !== 6) {
        msg.textContent = '❌ Please enter the 6-digit code';
        msg.className = 'otp-error';
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Verifying...';

    try {
        const res = await fetch('/api/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        const data = await res.json();

        if (data.success) {
            msg.textContent = '✅ ' + data.message + ' Logging you in...';
            msg.className = 'otp-success';
            setTimeout(() => location.reload(), 1500);
        } else {
            msg.textContent = '❌ ' + data.error;
            msg.className = 'otp-error';
            btn.disabled = false;
            btn.textContent = 'Verify ✅';
        }
    } catch (e) {
        msg.textContent = '❌ Connection error. Please try again.';
        msg.className = 'otp-error';
        btn.disabled = false;
        btn.textContent = 'Verify ✅';
    }
}

// Allow pressing Enter to submit OTP
document.addEventListener('DOMContentLoaded', () => {
    const otpCode = document.getElementById('otpCode');
    if (otpCode) {
        otpCode.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') verifyOTP();
        });
    }
    const loginEmail = document.getElementById('loginEmail');
    if (loginEmail) {
        loginEmail.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendOTP();
        });
    }
});
