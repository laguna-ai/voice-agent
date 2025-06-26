// widget/widget.js

import { getOrGenerateSessionId, sendMessageToBot, sendAudioToWhisper, getTTSFromText } from './apiService.js';
import { addMessage, showTypingIndicator, hideTypingIndicator, initWidget, playAudioFromBlob } from './domUtils.js';

export function initializeWidget() {
    // DOM Elements
    const closeChat = document.getElementById('close-chat');
    const minimizeChat = document.getElementById('minimize-chat');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const typingIndicator = document.getElementById('typing-indicator');
    const suggestionsToggle = document.getElementById('suggestions-toggle');
    const quickSuggestions = document.getElementById('quick-suggestions');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    const resetSessionBtn = document.getElementById('reset-session');
    const micButton = document.getElementById('mic-button');
    let mediaRecorder = null;
    let audioChunks = [];

    // Estado
    let isTyping = false;
    let suggestionsVisible = false;
    let chatHistory = [];
    //const URL_PREFIX = 'https://funciones-voice-emg9ducuaya8cyb3.eastus-01.azurewebsites.net/api';
    const URL_PREFIX = 'http://localhost:7071/api'
    const CHATBOT_API_URL = `${URL_PREFIX}/webhook`;
    const TTS_API_URL = `${URL_PREFIX}/tts`;
    const WHISPER_API_URL = `${URL_PREFIX}/transcribe`;
    
    const sessionId = getOrGenerateSessionId();
    
    const initialMessages = [
        '¡Bienvenido a tu experiencia Learnia! ¿Tienes dudas sobre el contenido, las actividades o la plataforma? Estoy para ti.',
        '¡Hola! ¿Listo para aprender? Puedo ayudarte con preguntas sobre tus cursos, evaluaciones o cómo avanzar más rápido.',
        '¡Hola! ¿Tienes preguntas sobre tu progreso, evaluaciones o próximas fechas clave? Pregúntame lo que quieras.'
    ];

    // Selecciona uno al azar
    const randomInitialMessage = initialMessages[Math.floor(Math.random() * initialMessages.length)];


    // Configuración
    const widgetConfig = {
        apiEndpoint: CHATBOT_API_URL,
        initialMessage:  randomInitialMessage
    };
    
    // Inicializar widget
    initWidget(widgetConfig);
    
    // Close Chat
    if (closeChat) {
        closeChat.addEventListener('click', function() {
            alert('Función de cerrar implementada en la versión completa');
        });
    }
    
    // Minimize Chat
    if (minimizeChat) {
        minimizeChat.addEventListener('click', function() {
            alert('Función de minimizar implementada en la versión completa');
        });
    }
    
    // Reset Session
    if (resetSessionBtn) {
        resetSessionBtn.addEventListener('click', function () {
            sessionStorage.removeItem('chatbotSessionId');
            location.reload(); // Opcional: recarga para reiniciar todo
        });
    }


    // Toggle Quick Suggestions
    if (suggestionsToggle) {
        suggestionsToggle.addEventListener('click', function() {
            suggestionsVisible = !suggestionsVisible;
            if (suggestionsVisible) {
                quickSuggestions.classList.remove('hidden');
                suggestionsToggle.innerHTML = '<i class="fas fa-chevron-up mr-1"></i> Ocultar';
            } else {
                quickSuggestions.classList.add('hidden');
                suggestionsToggle.innerHTML = '<i class="fas fa-lightbulb mr-1"></i> Sugerencias';
            }
        });
    }
    
    // --- Lógica de micrófono ---
    if (micButton) {
        micButton.addEventListener('click', async function() {
            const micIcon = micButton.querySelector('i');
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                micButton.classList.remove('bg-red-600');
                micButton.classList.remove('hover:bg-red-400');
                micButton.classList.add('bg-primary-500');
                micButton.classList.add('hover:bg-primary-600');
                if (micIcon) {
                    micIcon.classList.remove('fa-stop');
                    micIcon.classList.add('fa-microphone');
                }
                return;
            }
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Tu navegador no soporta grabación de audio');
                return;
            }
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new window.MediaRecorder(stream);
                audioChunks = [];
                mediaRecorder.ondataavailable = e => {
                    if (e.data.size > 0) audioChunks.push(e.data);
                };
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    addMessage('Procesando audio...', 'user', chatMessages);
                    showTypingIndicator(typingIndicator, chatMessages);
                    isTyping = true;
                    try {
                        const transcribedText = await sendAudioToWhisper(audioBlob, WHISPER_API_URL);
                        addMessage(transcribedText, 'user', chatMessages);
                        await handleBotResponse(transcribedText);
                    } catch (err) {
                        addMessage('No se pudo transcribir el audio.', 'bot', chatMessages);
                    } finally {
                        hideTypingIndicator(typingIndicator);
                        isTyping = false;
                    }
                };
                mediaRecorder.start();
                micButton.classList.remove('bg-primary-500');
                micButton.classList.remove('hover:bg-primary-600');
                micButton.classList.add('bg-red-600');
                micButton.classList.add('hover:bg-red-400');
                if (micIcon) {
                    micIcon.classList.remove('fa-microphone');
                    micIcon.classList.add('fa-stop');
                }
            } catch (err) {
                alert('No se pudo acceder al micrófono.');
            }
        });
    }

    // --- Lógica para manejar respuesta del bot y reproducir TTS ---
    async function handleBotResponse(message) {
        // Show typing indicator
        showTypingIndicator(typingIndicator, chatMessages);
        isTyping = true;
        try {
            const { botMessage, updatedHistory } = await sendMessageToBot(
                message,
                sessionId,
                CHATBOT_API_URL,
                chatHistory
            );
            chatHistory = updatedHistory;
            addMessage(botMessage, 'bot', chatMessages);
            // Pedir audio TTS y reproducirlo
            try {
                const audioBlob = await getTTSFromText(botMessage, TTS_API_URL);
                playAudioFromBlob(audioBlob);
            } catch (err) {
                // Si falla el TTS, solo mostrar texto
            }
        } catch (error) {
            addMessage('Error de conexión. Por favor, intenta de nuevo.', 'bot', chatMessages);
        } finally {
            hideTypingIndicator(typingIndicator);
            isTyping = false;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Send Message
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '' || isTyping) return;
        
        // Add user message to chat
        addMessage(message, 'user', chatMessages);
        userInput.value = '';
        
        // Hide suggestions if visible
        if (suggestionsVisible && quickSuggestions) {
            quickSuggestions.classList.add('hidden');
            suggestionsVisible = false;
            suggestionsToggle.innerHTML = '<i class="fas fa-lightbulb mr-1"></i> Sugerencias';
        }
        
        await handleBotResponse(message);
    }
    
    // Handle suggestion button clicks
    if (suggestionBtns.length > 0) {
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                if (userInput) {
                    userInput.value = this.textContent.trim();
                    userInput.focus();
                }
            });
        });
    }
    
    // Event Listeners
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}