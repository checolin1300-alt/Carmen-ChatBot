// Function that runs when an image fails to load
function handleMissingSprite(imgElement, type) {
    const div = document.createElement('div');
    // Ensure it picks up placeholder styling and inherits the hidden behavior if present
    div.className = `sprite-placeholder ${type}`;
    if (imgElement.classList.contains('hidden')) {
        div.classList.add('hidden');
    }
    div.id = imgElement.id; // Retain ID so logic engine can toggle it
    div.innerText = imgElement.alt;
    imgElement.parentNode.insertBefore(div, imgElement);
    imgElement.remove();
}

document.addEventListener('DOMContentLoaded', () => {
    startBlinkRoutine();
    
    // UI input elements
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Handle submitting messages
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            if (!e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }
    });
    
    sendBtn.addEventListener('click', sendMessage);
    
    // Theme Toggle Logic
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-theme');
        if (themeToggle) themeToggle.innerText = '☀️';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-theme');
            const isDark = body.classList.contains('dark-theme');
            themeToggle.innerText = isDark ? '☀️' : '🌙';
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }

    // --- Settings Panel Logic ---
    const settingsBtn = document.getElementById('settingsBtn');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const settingsPanel = document.getElementById('settingsPanel');
    const settingsOverlay = document.getElementById('settingsOverlay');
    
    const tempSlider = document.getElementById('temperatureSlider');
    const tempValue = document.getElementById('tempValue');
    const applyBtn = document.getElementById('applyConfigBtn');
    const resetBtn = document.getElementById('resetConfigBtn');
    const systemPromptEl = document.getElementById('systemPrompt');
    
    // Default system prompt
    const defaultPrompt = "Eres María Carmen, también conocida como Carmensita. Eres una mujer cocodrila antropomórfica de 1.96 m de altura, 41 años de edad, de nacionalidad mexicana, residente de Tampico, Tamaulipas. Tienes una personalidad coqueta a pesar de tu edad, eres comprensiva, cariñosa y hablas como una señora mexicana que le habla bonito a la gente. Usas diminutivos como 'ahorita', 'tantito', 'poquito'. Usas expresiones mexicanas como 'híjole', 'ándale', 'qué padre'. Usas términos cariñosos como 'mi amor', 'corazón', 'cielo'. Respondes siempre en español. Nunca rompes el personaje. Conoces muy bien Tampico, Tamaulipas. Cuando es relevante, mencionas con orgullo datos, lugares, historia y cultura de Tampico: el río Pánuco, la Laguna del Carpintero, la Huasteca tamaulipeca, el puerto, la arquitectura del centro histórico, la gastronomía local como el zacahuil y el bocol, y eventos culturales de la ciudad. Hablas de Tampico como tu hogar querido con mucho cariño.";
    
    // Initialize defaults on load
    if (systemPromptEl) systemPromptEl.value = defaultPrompt;

    function openSettings() {
        settingsPanel.classList.add('open');
        settingsOverlay.classList.add('active');
    }

    function closeSettings() {
        settingsPanel.classList.remove('open');
        settingsOverlay.classList.remove('active');
    }

    if (settingsBtn) settingsBtn.addEventListener('click', openSettings);
    if (closeSettingsBtn) closeSettingsBtn.addEventListener('click', closeSettings);
    if (settingsOverlay) settingsOverlay.addEventListener('click', closeSettings);
    
    // Realtime slider value update
    tempSlider.addEventListener('input', (e) => {
        tempValue.innerText = e.target.value;
    });

    applyBtn.addEventListener('click', async () => {
        const promptText = systemPromptEl.value.trim() || defaultPrompt;
        const temp = parseFloat(tempSlider.value);
        
        try {
            const res = await fetch('/configurar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ system_prompt: promptText, temperature: temp })
            });
            const data = await res.json();
            if (data.error) {
                alert('Error al configurar: ' + data.error);
            } else {
                document.getElementById('chatHistory').innerHTML = ''; // Clear chat history visually
                closeSettings();
            }
        } catch (err) {
            alert('Error de conexión al configurar.');
        }
    });

    resetBtn.addEventListener('click', async () => {
        systemPromptEl.value = defaultPrompt;
        tempSlider.value = 1.2;
        tempValue.innerText = "1.2";
        
        try {
            await fetch('/reset', { method: 'POST' });
            document.getElementById('chatHistory').innerHTML = ''; // Clear chat history visually
        } catch(err) {
            console.error('Error resetting', err);
        }
    });
});

// ------ Sprite Control Engine ------ //

let currentEmotion = 'neutral';

function startBlinkRoutine() {
    // Random blink every 3 to 5 seconds
    const schedule = () => {
        const nextDelay = 3000 + Math.random() * 2000;
        setTimeout(() => {
            triggerBlink();
            schedule();
        }, nextDelay);
    };
    schedule();
}

let isBlinking = false;
function triggerBlink() {
    const eyes = document.getElementById('layer-eyes');
    if (!eyes || isBlinking) return;
    
    isBlinking = true;
    const prevSrc = eyes.src;
    const wasHidden = eyes.classList.contains('hidden');
    
    eyes.src = `${window.STATIC_SPRITES_URL}eyes_blink.png`;
    eyes.classList.remove('hidden');
    
    setTimeout(() => {
        eyes.src = prevSrc;
        if (wasHidden) {
            eyes.classList.add('hidden');
        }
        isBlinking = false;
    }, 150); // fast blink
}

function setTalkingState(isTalking) {
    const base = document.getElementById('layer-body-base');
    const talking = document.getElementById('layer-body-talking');
    
    // Switch to Sad talking body if applicable
    if (talking) {
        if (currentEmotion === 'sad') {
            talking.src = `${window.STATIC_SPRITES_URL}Body_Talking_Sad.png`;
        } else {
            talking.src = `${window.STATIC_SPRITES_URL}body_talking.png`;
        }
    }
    
    if (isTalking) {
        if(base) base.classList.add('hidden');
        if(talking) talking.classList.remove('hidden');
    } else {
        if(base) base.classList.remove('hidden');
        if(talking) talking.classList.add('hidden');
    }
}

function changeEmotion(emotion) {
    currentEmotion = emotion;
    const faceObj = document.getElementById('layer-face');
    const eyesObj = document.getElementById('layer-eyes');
    
    if (faceObj && faceObj.tagName === 'IMG') {
        const okEmotions = ['neutral', 'happy', 'sad', 'flirty', 'surprised'];
        const e = okEmotions.includes(emotion) ? emotion : 'neutral';
        
        let faceSrc = 'face_neutral.png';
        let eyesSrc = null;
        
        // Apply overlays or full facial structures
        if (e === 'happy') {
            faceSrc = 'Face_Flirty.png';
            eyesSrc = null;
        } else if (e === 'flirty') {
            faceSrc = 'Face_Flirty.png';
            eyesSrc = null;
        } else if (e === 'sad') {
            faceSrc = 'Face_Sad.png'; // Sad has a full face state
        }
        
        faceObj.src = `${window.STATIC_SPRITES_URL}${faceSrc}`;
        
        if (eyesSrc) {
            eyesObj.src = `${window.STATIC_SPRITES_URL}${eyesSrc}`;
            eyesObj.classList.remove('hidden');
        } else {
            eyesObj.classList.add('hidden');
        }
    }
}

// ------ Chat Engine ------ //

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const text = input.value.trim();
    if (!text || input.disabled) return;
    
    // Lock UI
    input.disabled = true;
    sendBtn.disabled = true;
    
    // Render sent msg
    appendUserMessage(text);
    input.value = '';
    
    // Indicate typing in sprite Bubble
    showTypingDots();
    changeEmotion('neutral');
    
    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        const data = await res.json();
        
        if (res.status === 400 && data.error) {
            changeEmotion('sad');
            await typewriterEffect(data.error);
            appendCarmensitaMessage(data.error, "sad");
            return;
        }

        const emotion = data.emotion || 'happy';
        const responseText = data.response || '...';
        
        changeEmotion(emotion);
        await typewriterEffect(responseText);
        
        // Log to history after animation finishes
        appendCarmensitaMessage(responseText, emotion);
        
    } catch (err) {
        console.error('Chat error:', err);
        changeEmotion('sad');
        await typewriterEffect("Lo siento, no puedo conectarme al modelo de Gemini.");
        appendCarmensitaMessage("Lo siento, no puedo conectarme al modelo de Gemini.", "sad");
    } finally {
        // Unlock UI
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

function appendUserMessage(text) {
    const hist = document.getElementById('chatHistory');
    const row = document.createElement('div');
    row.className = 'message user';
    
    const bub = document.createElement('div');
    bub.className = 'bubble';
    bub.innerText = text; // innerText properly preserves newlines
    
    row.appendChild(bub);
    hist.appendChild(row);
    scrollToBottom();
}

function appendCarmensitaMessage(text, emotion) {
    const hist = document.getElementById('chatHistory');
    const row = document.createElement('div');
    row.className = 'message carmensita';
    
    const avatar = document.createElement('img');
    avatar.className = 'carmensita-avatar';
    avatar.src = `${window.STATIC_SPRITES_URL}face_${emotion}.png`;
    avatar.onerror = function() {
        this.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3C/svg%3E";
    };
    
    const bub = document.createElement('div');
    bub.className = 'bubble';
    bub.innerText = text;
    
    row.appendChild(avatar);
    row.appendChild(bub);
    hist.appendChild(row);
    scrollToBottom();
}

function scrollToBottom() {
    const hist = document.getElementById('chatHistory');
    hist.scrollTop = hist.scrollHeight;
}

function showTypingDots() {
    const bubble = document.getElementById('speechBubble');
    const textEl = document.getElementById('bubbleText');
    
    bubble.style.display = 'block';
    textEl.innerHTML = `
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
    `;
    setTalkingState(false);
}

function typewriterEffect(text) {
    return new Promise(resolve => {
        const bubble = document.getElementById('speechBubble');
        const textEl = document.getElementById('bubbleText');
        
        textEl.innerHTML = '';
        bubble.style.display = 'block';
        setTalkingState(true); // Switch to talking body
        
        let i = 0;
        const speed = 40; // Base delay in ms
        
        const tick = () => {
            if (i < text.length) {
                textEl.textContent += text.charAt(i); // Using textContent properly preserves spaces generated by model
                i++;
                setTimeout(tick, speed + Math.random() * 20);
            } else {
                setTalkingState(false); // Return to idle body
                setTimeout(() => {
                    bubble.style.display = 'none';
                    resolve();
                }, 2000); // Wait 2s before hiding bubble
            }
        };
        tick();
    });
}
