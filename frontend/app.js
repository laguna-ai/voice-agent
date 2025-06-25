// app.js - Funcionalidades para app

document.addEventListener('DOMContentLoaded', function() {
    // Efecto hover para las tarjetas de características
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Simulación de actividad del chatbot
    const statusDot = document.querySelector('.status-dot');
    const chatStatus = document.querySelector('.chat-status');
    
    setInterval(() => {
        const messages = [
            'En línea',
            'Aprendiendo ...',
            'Procesando ...',
            'Listo para ayudar'
        ];
        
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        chatStatus.innerHTML = `<div class="status-dot"></div>${randomMessage}`;
    }, 5000);

    
});

