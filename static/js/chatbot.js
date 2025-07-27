// AI Medical Assistant Chatbot
// Medical Report Management System

class MedicalChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendMessage');
        this.isProcessing = false;
        
        this.initializeEventListeners();
        this.scrollToBottom();
    }
    
    initializeEventListeners() {
        // Send button click
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        // Enter key press
        if (this.chatInput) {
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Auto-resize input
            this.chatInput.addEventListener('input', () => {
                this.autoResizeInput();
            });
        }
        
        // Focus input when chat area is clicked
        if (this.chatMessages) {
            this.chatMessages.addEventListener('click', () => {
                if (this.chatInput) {
                    this.chatInput.focus();
                }
            });
        }
    }
    
    autoResizeInput() {
        if (this.chatInput) {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
        }
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        
        if (!message || this.isProcessing) {
            return;
        }
        
        // Clear input and disable controls
        this.chatInput.value = '';
        this.autoResizeInput();
        this.setProcessingState(true);
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        try {
            // Send request to backend
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add bot response to chat
            this.addMessage(data.response, 'bot');
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.addMessage(
                `Sorry, I encountered an error: ${error.message}. Please try again.`,
                'bot',
                true
            );
        } finally {
            this.setProcessingState(false);
        }
    }
    
    addMessage(content, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (isError) {
            messageContent.classList.add('error-message');
        }
        
        // Add sender label and timestamp
        const senderLabel = document.createElement('small');
        senderLabel.className = 'text-muted d-block mb-1';
        senderLabel.textContent = sender === 'user' ? 'You' : 'AI Assistant';
        
        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp ms-2';
        timestamp.textContent = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        senderLabel.appendChild(timestamp);
        
        // Format message content
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(content);
        
        messageContent.appendChild(senderLabel);
        messageContent.appendChild(messageText);
        messageDiv.appendChild(messageContent);
        
        // Add to chat
        this.chatMessages.appendChild(messageDiv);
        
        // Animate in
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
        
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Convert line breaks to HTML
        let formatted = content.replace(/\n/g, '<br>');
        
        // Bold formatting for **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Bullet points
        formatted = formatted.replace(/^• /gm, '<i class="fas fa-circle me-1" style="font-size: 0.5rem;"></i>');
        
        // Patient ID highlighting
        formatted = formatted.replace(/Patient ID (\d+)/g, '<span class="badge bg-primary">Patient ID $1</span>');
        
        // Disease highlighting
        const diseases = [
            'cancer', 'diabetes', 'hypertension', 'heart', 'lung', 'kidney',
            'liver', 'brain', 'blood', 'infection', 'fever', 'flu', 'covid',
            'pneumonia', 'asthma', 'arthritis', 'depression', 'anxiety'
        ];
        
        diseases.forEach(disease => {
            const regex = new RegExp(`\\b(${disease})\\b`, 'gi');
            formatted = formatted.replace(regex, '<span class="text-primary fw-semibold">$1</span>');
        });
        
        return formatted;
    }
    
    setProcessingState(processing) {
        this.isProcessing = processing;
        
        if (this.chatInput) {
            this.chatInput.disabled = processing;
            this.chatInput.placeholder = processing ? 'Processing...' : 'Ask about patients...';
        }
        
        if (this.sendButton) {
            this.sendButton.disabled = processing;
            
            if (processing) {
                this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                this.addTypingIndicator();
            } else {
                this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
                this.removeTypingIndicator();
                this.chatInput.focus();
            }
        }
    }
    
    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `
            <small class="text-muted">AI Assistant is typing</small>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        typingDiv.appendChild(messageContent);
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    scrollToBottom() {
        if (this.chatMessages) {
            setTimeout(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }, 100);
        }
    }
    
    // Quick action buttons
    addQuickActions() {
        const quickActions = [
            { text: 'Show all patients', icon: 'fas fa-users' },
            { text: 'Count total patients', icon: 'fas fa-calculator' },
            { text: 'Show disease stats', icon: 'fas fa-chart-bar' },
            { text: 'Help', icon: 'fas fa-question-circle' }
        ];
        
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'quick-actions mt-2 mb-2';
        actionsDiv.innerHTML = '<small class="text-muted">Quick actions:</small>';
        
        quickActions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'btn btn-sm btn-outline-primary me-1 mb-1';
            button.innerHTML = `<i class="${action.icon} me-1"></i>${action.text}`;
            button.addEventListener('click', () => {
                this.chatInput.value = action.text;
                this.sendMessage();
            });
            actionsDiv.appendChild(button);
        });
        
        // Insert after initial message
        const firstMessage = this.chatMessages.querySelector('.chat-message');
        if (firstMessage && firstMessage.nextSibling) {
            this.chatMessages.insertBefore(actionsDiv, firstMessage.nextSibling);
        } else {
            this.chatMessages.appendChild(actionsDiv);
        }
    }
    
    // Search integration
    searchPatients(query) {
        // If dashboard.js is available, use its filtering function
        if (typeof filterPatients === 'function') {
            filterPatients(query);
            
            // Scroll to patients section
            const patientsContainer = document.getElementById('patientsContainer');
            if (patientsContainer) {
                patientsContainer.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    }
    
    // Handle special commands
    handleSpecialCommands(message) {
        const lowerMessage = message.toLowerCase();
        
        // Clear chat command
        if (lowerMessage === 'clear' || lowerMessage === 'clear chat') {
            this.clearChat();
            return true;
        }
        
        // Export command
        if (lowerMessage.includes('export') && typeof exportPatientData === 'function') {
            exportPatientData();
            this.addMessage('Patient data has been exported to CSV.', 'bot');
            return true;
        }
        
        return false;
    }
    
    clearChat() {
        // Keep only the initial welcome message
        const messages = this.chatMessages.querySelectorAll('.chat-message');
        for (let i = 1; i < messages.length; i++) {
            messages[i].remove();
        }
        
        // Remove quick actions if they exist
        const quickActions = this.chatMessages.querySelector('.quick-actions');
        if (quickActions) {
            quickActions.remove();
        }
        
        this.addMessage('Chat cleared. How can I help you?', 'bot');
    }
    
    // Initialize chatbot with enhanced features
    initialize() {
        // Add quick actions after a short delay
        setTimeout(() => {
            this.addQuickActions();
        }, 1000);
        
        // Add CSS for typing indicator
        this.addTypingIndicatorStyles();
        
        // Add error message styles
        this.addErrorMessageStyles();
        
        console.log('Medical chatbot initialized');
    }
    
    addTypingIndicatorStyles() {
        if (document.getElementById('chatbot-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'chatbot-styles';
        style.textContent = `
            .typing-dots {
                display: inline-flex;
                align-items: center;
                gap: 3px;
                margin-left: 5px;
            }
            
            .typing-dots span {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background-color: var(--primary-color, #87CEEB);
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
            .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
            
            @keyframes typing {
                0%, 80%, 100% {
                    transform: scale(0.8);
                    opacity: 0.5;
                }
                40% {
                    transform: scale(1);
                    opacity: 1;
                }
            }
            
            .error-message {
                background-color: #f8d7da !important;
                border-color: #f5c6cb !important;
                color: #721c24 !important;
            }
            
            .quick-actions button {
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
            }
            
            .message-text {
                word-wrap: break-word;
                line-height: 1.4;
            }
            
            .timestamp {
                font-size: 0.7rem;
                opacity: 0.7;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    addErrorMessageStyles() {
        // Error message styles are included in the typing indicator styles
    }
}

// Utility functions for chatbot integration
function initializeChatbot() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            const chatbot = new MedicalChatbot();
            chatbot.initialize();
        });
    } else {
        const chatbot = new MedicalChatbot();
        chatbot.initialize();
    }
}

// Enhanced search functionality
function enhancedPatientSearch(query) {
    const results = {
        patients: [],
        diseases: [],
        total: 0
    };
    
    const patientCards = document.querySelectorAll('.patient-card');
    const searchLower = query.toLowerCase();
    
    patientCards.forEach(card => {
        const patientId = card.dataset.patientId;
        const diseases = card.dataset.diseases;
        const patientName = card.querySelector('h6').textContent.toLowerCase();
        
        if (patientId.includes(query) || 
            diseases.includes(searchLower) || 
            patientName.includes(searchLower)) {
            
            results.patients.push({
                id: patientId,
                name: patientName,
                diseases: diseases.split(' ')
            });
            
            // Collect unique diseases
            diseases.split(' ').forEach(disease => {
                if (disease && !results.diseases.includes(disease)) {
                    results.diseases.push(disease);
                }
            });
        }
    });
    
    results.total = results.patients.length;
    return results;
}

// Voice input support (if Web Speech API is available)
function initializeVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        return; // Speech recognition not supported
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    // Add voice input button
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        const voiceButton = document.createElement('button');
        voiceButton.type = 'button';
        voiceButton.className = 'btn btn-outline-secondary btn-sm ms-1';
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.title = 'Voice input';
        
        voiceButton.addEventListener('click', () => {
            recognition.start();
            voiceButton.innerHTML = '<i class="fas fa-microphone text-danger"></i>';
        });
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        };
        
        recognition.onerror = () => {
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        };
        
        recognition.onend = () => {
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        };
        
        chatInput.parentNode.appendChild(voiceButton);
    }
}

// Initialize everything when the script loads
initializeChatbot();

// Initialize voice input if available
document.addEventListener('DOMContentLoaded', () => {
    initializeVoiceInput();
});

// Export for use in other scripts
window.MedicalChatbot = MedicalChatbot;
window.enhancedPatientSearch = enhancedPatientSearch;
