// Campus Sustainability AI Chatbot

class SustainabilityChatbot {
    constructor() {
        this.messages = [];
        this.isOpen = false;
        this.isTyping = false;
        this.isListening = false;
        this.recognition = null;
        this.init();
        this.initVoiceRecognition();
    }

    init() {
        this.createChatbotWidget();
        this.attachEventListeners();
        this.showWelcomeMessage();
    }

    createChatbotWidget() {
        const widget = document.createElement('div');
        widget.className = 'chatbot-widget';
        widget.innerHTML = `
            <button class="chatbot-toggle" id="chatbot-toggle">
                <i class="fas fa-comments"></i>
            </button>
            
            <div class="chatbot-window" id="chatbot-window">
                <div class="chatbot-header">
                    <div class="chatbot-header-title">
                        <i class="fas fa-robot"></i>
                        <div>
                            <h5>Sustainability Assistant</h5>
                            <div class="chatbot-header-subtitle">Ask me anything!</div>
                        </div>
                    </div>
                    <button class="chatbot-close" id="chatbot-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="chatbot-messages" id="chatbot-messages">
                    <!-- Messages will be added here -->
                </div>
                
                <div class="chatbot-suggestions" id="chatbot-suggestions">
                    <div class="chatbot-suggestions-title">Suggested questions:</div>
                    <div class="chatbot-suggestion-chips" id="chatbot-suggestion-chips">
                        <!-- Suggestions will be added here -->
                    </div>
                </div>
                
                <div class="chatbot-input-area">
                    <div class="chatbot-input-wrapper">
                        <button class="chatbot-voice-btn" id="chatbot-voice-btn" title="Voice input">
                            <i class="fas fa-microphone"></i>
                        </button>
                        <input
                            type="text"
                            class="chatbot-input"
                            id="chatbot-input"
                            placeholder="Type or speak your question..."
                            autocomplete="off"
                        />
                        <button class="chatbot-send-btn" id="chatbot-send-btn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(widget);
    }

    attachEventListeners() {
        const toggle = document.getElementById('chatbot-toggle');
        const close = document.getElementById('chatbot-close');
        const sendBtn = document.getElementById('chatbot-send-btn');
        const voiceBtn = document.getElementById('chatbot-voice-btn');
        const input = document.getElementById('chatbot-input');

        toggle.addEventListener('click', () => this.toggleChatbot());
        close.addEventListener('click', () => this.closeChatbot());
        sendBtn.addEventListener('click', () => this.sendMessage());
        voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        input.addEventListener('input', (e) => {
            this.handleInputChange(e.target.value);
        });
    }

    toggleChatbot() {
        this.isOpen = !this.isOpen;
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        if (this.isOpen) {
            window.classList.add('active');
            toggle.classList.add('active');
            document.getElementById('chatbot-input').focus();
        } else {
            window.classList.remove('active');
            toggle.classList.remove('active');
        }
    }

    closeChatbot() {
        this.isOpen = false;
        document.getElementById('chatbot-window').classList.remove('active');
        document.getElementById('chatbot-toggle').classList.remove('active');
    }

    showWelcomeMessage() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.innerHTML = `
            <div class="chatbot-welcome">
                <div class="chatbot-welcome-icon">
                    <i class="fas fa-leaf"></i>
                </div>
                <h4>Welcome to Sustainability Assistant!</h4>
                <p>I can help you with campus sustainability questions, policies, and complaint resolution.</p>
                
                <div class="chatbot-quick-questions">
                    <div class="chatbot-quick-question" onclick="chatbotInstance.askQuestion('How can I report a water leak?')">
                        💧 How can I report a water leak?
                    </div>
                    <div class="chatbot-quick-question" onclick="chatbotInstance.askQuestion('What are the energy saving tips?')">
                        ⚡ What are the energy saving tips?
                    </div>
                    <div class="chatbot-quick-question" onclick="chatbotInstance.askQuestion('How do I submit a complaint?')">
                        📝 How do I submit a complaint?
                    </div>
                    <div class="chatbot-quick-question" onclick="chatbotInstance.askQuestion('What are sustainable transportation options?')">
                        🚌 What are sustainable transportation options?
                    </div>
                </div>
            </div>
        `;
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const question = input.value.trim();
        
        if (!question) return;
        
        // Clear input
        input.value = '';
        
        // Hide suggestions
        document.getElementById('chatbot-suggestions').classList.remove('active');
        
        // Add user message
        this.addMessage(question, 'user');
        
        // Show typing indicator
        this.showTyping();
        
        try {
            // Get token if available
            const token = localStorage.getItem('session_token');
            const headers = {
                'Content-Type': 'application/json'
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            
            // Send to API
            const response = await fetch('/api/chatbot/ask', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ question: question })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();
            
            if (data.success) {
                this.addMessage(data.response, 'bot', data.source);
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTyping();
            this.addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'bot');
        }
    }

    askQuestion(question) {
        if (!this.isOpen) {
            this.toggleChatbot();
        }
        
        // Wait for animation
        setTimeout(() => {
            document.getElementById('chatbot-input').value = question;
            this.sendMessage();
        }, 300);
    }

    addMessage(text, sender, source = null) {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        // Remove welcome message if exists
        const welcome = messagesContainer.querySelector('.chatbot-welcome');
        if (welcome) {
            welcome.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}`;
        
        const time = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const avatar = sender === 'bot' ? 
            '<i class="fas fa-robot"></i>' : 
            '<i class="fas fa-user"></i>';
        
        messageDiv.innerHTML = `
            <div class="chatbot-message-avatar">${avatar}</div>
            <div class="chatbot-message-content">
                <div class="chatbot-message-bubble">${this.formatMessage(text)}</div>
                <div class="chatbot-message-time">${time}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        this.messages.push({ text, sender, time, source });
    }

    formatMessage(text) {
        // Convert newlines to <br>
        text = text.replace(/\n/g, '<br>');
        
        // Convert bullet points
        text = text.replace(/•/g, '&bull;');
        
        // Make URLs clickable
        text = text.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank">$1</a>'
        );
        
        return text;
    }

    showTyping() {
        this.isTyping = true;
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatbot-message bot';
        typingDiv.id = 'chatbot-typing-indicator';
        typingDiv.innerHTML = `
            <div class="chatbot-message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="chatbot-message-content">
                <div class="chatbot-typing">
                    <div class="chatbot-typing-dot"></div>
                    <div class="chatbot-typing-dot"></div>
                    <div class="chatbot-typing-dot"></div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('chatbot-typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async handleInputChange(value) {
        if (value.length > 3) {
            try {
                const response = await fetch('/api/chatbot/suggestions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ partial: value })
                });
                
                const data = await response.json();
                
                if (data.success && data.suggestions.length > 0) {
                    this.showSuggestions(data.suggestions);
                }
            } catch (error) {
                console.error('Suggestions error:', error);
            }
        } else {
            this.hideSuggestions();
        }
    }

    showSuggestions(suggestions) {
        const suggestionsContainer = document.getElementById('chatbot-suggestions');
        const chipsContainer = document.getElementById('chatbot-suggestion-chips');
        
        chipsContainer.innerHTML = suggestions.map(suggestion => 
            `<div class="chatbot-suggestion-chip" onclick="chatbotInstance.selectSuggestion('${this.escapeHtml(suggestion)}')">${suggestion}</div>`
        ).join('');
        
        suggestionsContainer.classList.add('active');
    }

    hideSuggestions() {
        document.getElementById('chatbot-suggestions').classList.remove('active');
    }

    selectSuggestion(suggestion) {
        document.getElementById('chatbot-input').value = suggestion;
        this.hideSuggestions();
        document.getElementById('chatbot-input').focus();
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    initVoiceRecognition() {
        // Check if browser supports speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('Speech recognition not supported in this browser');
            // Hide voice button if not supported
            setTimeout(() => {
                const voiceBtn = document.getElementById('chatbot-voice-btn');
                if (voiceBtn) {
                    voiceBtn.style.display = 'none';
                }
            }, 100);
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;  // Keep listening
        this.recognition.interimResults = true;  // Show interim results
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;
        
        let finalTranscript = '';
        let interimTranscript = '';
        
        this.recognition.onstart = () => {
            console.log('[Voice] Recognition started');
            this.isListening = true;
            finalTranscript = '';
            interimTranscript = '';
            
            const voiceBtn = document.getElementById('chatbot-voice-btn');
            if (voiceBtn) {
                voiceBtn.classList.add('listening');
                voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                voiceBtn.title = 'Stop listening';
            }
            
            const input = document.getElementById('chatbot-input');
            if (input) {
                input.placeholder = '🎤 Listening... Speak now!';
                input.classList.add('listening');
            }
        };
        
        this.recognition.onresult = (event) => {
            interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                    console.log('[Voice] Final:', transcript);
                } else {
                    interimTranscript += transcript;
                    console.log('[Voice] Interim:', transcript);
                }
            }
            
            const input = document.getElementById('chatbot-input');
            if (input) {
                // Show both final and interim results
                input.value = (finalTranscript + interimTranscript).trim();
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('[Voice] Error:', event.error);
            
            if (event.error === 'no-speech') {
                console.log('[Voice] No speech detected, continuing...');
                // Don't stop, just continue listening
                return;
            }
            
            this.stopVoiceInput();
            
            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                this.showVoiceMessage('🎤 Microphone access denied. Please enable it in browser settings.');
            } else if (event.error === 'network') {
                this.showVoiceMessage('🌐 Network error. Please check your connection.');
            } else if (event.error === 'aborted') {
                console.log('[Voice] Recognition aborted');
            } else {
                this.showVoiceMessage('⚠️ Voice recognition error. Please try again.');
            }
        };
        
        this.recognition.onend = () => {
            console.log('[Voice] Recognition ended');
            
            // If we were listening and got a final transcript, auto-send
            if (this.isListening && finalTranscript.trim()) {
                const input = document.getElementById('chatbot-input');
                if (input && input.value.trim()) {
                    console.log('[Voice] Auto-sending message:', input.value);
                    // Small delay to ensure UI updates
                    setTimeout(() => {
                        this.sendMessage();
                    }, 300);
                }
            }
            
            this.stopVoiceInput();
        };
        
        console.log('[Voice] Recognition initialized');
    }
    
    toggleVoiceInput() {
        if (this.isListening) {
            console.log('[Voice] Stopping voice input');
            this.stopVoiceInput();
        } else {
            console.log('[Voice] Starting voice input');
            this.startVoiceInput();
        }
    }
    
    startVoiceInput() {
        if (!this.recognition) {
            this.showVoiceMessage('🎤 Voice input not supported in this browser. Please use Chrome, Edge, or Safari.');
            return;
        }
        
        // Request microphone permission first
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(() => {
                    console.log('[Voice] Microphone permission granted');
                    try {
                        this.recognition.start();
                        console.log('[Voice] Recognition started successfully');
                    } catch (error) {
                        console.error('[Voice] Error starting recognition:', error);
                        if (error.message.includes('already started')) {
                            console.log('[Voice] Recognition already running');
                        } else {
                            this.showVoiceMessage('⚠️ Could not start voice input. Please try again.');
                        }
                    }
                })
                .catch((error) => {
                    console.error('[Voice] Microphone permission denied:', error);
                    this.showVoiceMessage('🎤 Microphone access denied. Please enable it in browser settings.');
                });
        } else {
            // Fallback for browsers without getUserMedia
            try {
                this.recognition.start();
            } catch (error) {
                console.error('[Voice] Error starting recognition:', error);
                this.showVoiceMessage('⚠️ Could not start voice input. Please try again.');
            }
        }
    }
    
    stopVoiceInput() {
        this.isListening = false;
        
        const voiceBtn = document.getElementById('chatbot-voice-btn');
        if (voiceBtn) {
            voiceBtn.classList.remove('listening');
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.title = 'Voice input';
        }
        
        const input = document.getElementById('chatbot-input');
        if (input) {
            input.placeholder = 'Type or speak your question...';
            input.classList.remove('listening');
        }
        
        if (this.recognition) {
            try {
                this.recognition.stop();
                console.log('[Voice] Recognition stopped');
            } catch (error) {
                console.log('[Voice] Error stopping recognition:', error);
                // Ignore errors when stopping
            }
        }
    }
    
    showVoiceMessage(message) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-voice-message';
        messageDiv.textContent = message;
        messageDiv.style.cssText = 'text-align: center; padding: 10px; color: #666; font-size: 12px;';
        messagesContainer.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
        
        this.scrollToBottom();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is ready
let chatbotInstance;
document.addEventListener('DOMContentLoaded', function() {
    chatbotInstance = new SustainabilityChatbot();
});

// Made with Bob
