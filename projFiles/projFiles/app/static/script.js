/* Configuration */
const subjectsByClass = {
    Class_5_rag: ["science", "maths", "english_literature", "evs"],
    Class_6_rag: ["science", "maths", "english_literature", "history", "geography", "social_science"],
    Class_7_rag: ["science", "maths", "english_literature", "history", "geography", "civics"],
    Class_8_rag: ["science", "maths", "english_literature", "history", "geography", "civics"],
    Class_9_rag: ["biology", "chemistry", "physics", "history", "geography", "economics", "civics", "maths", "english_literature"],
    Class_10_rag: ["biology", "chemistry", "physics", "history", "geography", "economics", "civics", "maths", "english_literature"]
};

const classDisplayNames = {
    Class_5_rag: "Class 5",
    Class_6_rag: "Class 6",
    Class_7_rag: "Class 7",
    Class_8_rag: "Class 8",
    Class_9_rag: "Class 9",
    Class_10_rag: "Class 10"
};

const classDescriptions = {
    Class_5_rag: "Foundational concepts and introduction to core subjects.",
    Class_6_rag: "Expanding knowledge in science, math and languages.",
    Class_7_rag: "Advanced algebra, biology basics, and literature.",
    Class_8_rag: "Preparing for high school with deeper concepts.",
    Class_9_rag: "Core specialization in sciences and humanities.",
    Class_10_rag: "Board exam preparation and advanced specialization."
};

/* State */
let state = {
    currentView: 'gradeSelection', // matches keys in 'views'
    selectedClass: null,
    selectedSubject: null,
    userProfile: JSON.parse(localStorage.getItem('eduquest_user_profile')) || {
        name: "John Doe",
        email: "john.doe@school.edu",
        initials: "JD"
    }
};

/* DOM Elements */
// Keys match the state.currentView values for direct lookup
const views = {
    gradeSelection: document.getElementById('grade-selection'),
    subjectSelection: document.getElementById('subject-selection'),
    chat: document.getElementById('chat-view'),
    history: document.getElementById('history-view'),
    profile: document.getElementById('profile-view')
};

const containers = {
    gradeGrid: document.getElementById('grade-grid'),
    subjectGrid: document.getElementById('subject-grid'),
    chatMessages: document.getElementById('chat-messages'),
    historyList: document.getElementById('history-list')
};

const inputs = {
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn')
};

/* Init */
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    renderGradeSelection();
    initProfile(); // Add profile logic
    updateView(); // Ensure correct view is shown on load
    updateHeader();
});

/* Navigation */
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const target = e.currentTarget.dataset.target;

            // Remove active class from all nav items
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            e.currentTarget.classList.add('active');

            // Map data-target to state.currentView
            if (target === 'home') {
                state.selectedClass = null;
                state.selectedSubject = null;
                state.currentView = 'gradeSelection';
            } else if (target === 'history') {
                state.currentView = 'history';
                renderHistory();
            } else if (target === 'profile') {
                state.currentView = 'profile';
            } else if (target === 'change-grade') {
                state.selectedClass = null;
                state.selectedSubject = null;
                state.currentView = 'gradeSelection';
            } else if (target === 'change-subject') {
                if (state.selectedClass) {
                    state.selectedSubject = null;
                    state.currentView = 'subjectSelection';
                    renderSubjectSelection(state.selectedClass);
                } else {
                    alert('Please select a grade first.');
                    state.currentView = 'gradeSelection';
                    // Optional: highlight grade nav
                    document.querySelector('[data-target="change-grade"]').click();
                    return;
                }
            }

            updateView();
            updateHeader();
        });
    });

    // Chat input listeners
    inputs.sendBtn.addEventListener('click', sendMessage);
    inputs.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Voice Input Init
    initVoiceInput();
}

/* Voice Input Logic (Server-Side Trigger) */
function initVoiceInput() {
    const micBtn = document.getElementById('mic-btn');
    const chatInput = document.getElementById('chat-input');

    // Ensure button is visible
    micBtn.style.display = 'flex';

    micBtn.addEventListener('click', async () => {
        if (micBtn.classList.contains('listening')) return; // Prevent double click

        micBtn.classList.add('listening');
        const originalTitle = micBtn.title;
        micBtn.title = "Recording (5s)...";

        try {
            // Give user feedback in the input placeholder
            const oldPlaceholder = chatInput.placeholder;
            chatInput.placeholder = "🎤 Recording for 5 seconds...";

            // Call the server endpoint to record and transcribe
            const resp = await fetch('/listen', { method: 'POST' });
            const data = await resp.json();

            if (data.text) {
                const currentVal = chatInput.value;
                // Append text if input not empty, else set text
                chatInput.value = currentVal ? (currentVal + ' ' + data.text) : data.text;
                chatInput.focus();
            } else if (data.error) {
                console.error("Voice Error:", data.error);
                alert("Voice Error: " + data.error);
            } else {
                // No text returned (maybe silence)
                console.log("No text transcribed.");
            }

            chatInput.placeholder = oldPlaceholder;
        } catch (e) {
            console.error(e);
            alert("Could not connect to voice service.");
        } finally {
            micBtn.classList.remove('listening');
            micBtn.title = originalTitle;
        }
    });
}

function updateView() {
    // Hide all views
    Object.values(views).forEach(el => {
        if (el) el.classList.remove('active');
    });

    // Show current view based on state key
    const activeView = views[state.currentView];
    if (activeView) {
        activeView.classList.add('active');
    } else {
        console.error(`View not found for state: ${state.currentView}`);
    }
}

function updateHeader() {
    const headerTitle = document.getElementById('header-title');
    const headerBadge = document.getElementById('header-badge');

    if (state.currentView === 'gradeSelection') {
        headerTitle.textContent = 'Select Grade';
        headerBadge.style.display = 'none';
    } else if (state.currentView === 'subjectSelection') {
        headerTitle.textContent = 'Select Subject';
        headerBadge.style.display = 'block';
        headerBadge.textContent = classDisplayNames[state.selectedClass] || state.selectedClass;
    } else if (state.currentView === 'chat') {
        headerTitle.textContent = `${formatSubject(state.selectedSubject)} Assistant`;
        headerBadge.style.display = 'block';
        headerBadge.textContent = `${classDisplayNames[state.selectedClass]} • ${formatSubject(state.selectedSubject)}`;
    } else if (state.currentView === 'history') {
        headerTitle.textContent = 'Learning History';
        headerBadge.style.display = 'none';
    } else if (state.currentView === 'profile') {
        headerTitle.textContent = 'Profile';
        headerBadge.style.display = 'none';
    }
}

/* Renderers */
function renderGradeSelection() {
    const grid = containers.gradeGrid;
    grid.innerHTML = '';

    const classes = Object.keys(subjectsByClass);
    classes.forEach(cls => {
        const card = document.createElement('div');
        card.className = 'grade-card';
        // Extract number
        const num = cls.match(/\d+/)[0];

        card.innerHTML = `
            <div class="grade-number">${num}</div>
            <div class="grade-info">
                <h3>${classDisplayNames[cls]}</h3>
                <p>${classDescriptions[cls] || 'Curriculum concepts.'}</p>
            </div>
        `;
        card.addEventListener('click', () => {
            state.selectedClass = cls;
            state.currentView = 'subjectSelection'; // Updated to match key
            renderSubjectSelection(cls);
            updateView();
            updateHeader();
        });
        grid.appendChild(card);
    });
}

function renderSubjectSelection(cls) {
    const grid = containers.subjectGrid;
    grid.innerHTML = '';

    const subjects = subjectsByClass[cls] || [];
    subjects.forEach(sub => {
        const card = document.createElement('div');
        card.className = 'subject-card';
        card.textContent = formatSubject(sub);
        card.addEventListener('click', () => {
            state.selectedSubject = sub;
            state.currentView = 'chat'; // Updated to match key
            renderChat();
            updateView();
            updateHeader();
        });
        grid.appendChild(card);
    });
}

function renderChat() {
    const container = containers.chatMessages;
    container.innerHTML = '';

    // Add welcome message
    addMessageToChat(
        'bot',
        `Hello! I am your ${formatSubject(state.selectedSubject)} assistant for ${classDisplayNames[state.selectedClass]}. Ask me anything!`
    );
}

async function renderHistory() {
    const list = containers.historyList;
    list.innerHTML = '<div style="text-align: center; margin-top: 2rem;">Loading history...</div>';

    try {
        const resp = await fetch('/history');
        if (!resp.ok) throw new Error("Failed to fetch history");
        const historyData = await resp.json();

        list.innerHTML = '';

        if (historyData.length === 0) {
            list.innerHTML = '<div style="text-align: center; color: var(--text-secondary); margin-top:2rem;">No history yet.</div>';
            return;
        }

        historyData.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <div class="history-meta">
                    <span>${classDisplayNames[item.class] || item.class} • ${formatSubject(item.subject)}</span>
                    <span>${new Date(item.timestamp).toLocaleDateString()}</span>
                </div>
                <div class="history-query">${item.question}</div>
                <div class="history-preview">${item.answer.substring(0, 100)}...</div>
            `;
            list.appendChild(div);
        });

    } catch (e) {
        console.error(e);
        list.innerHTML = '<div style="text-align: center; color: red; margin-top:2rem;">Error loading history.</div>';
    }
}

/* Logic */
async function sendMessage() {
    const text = inputs.chatInput.value.trim();
    if (!text) return;

    // Add user message
    addMessageToChat('user', text);
    inputs.chatInput.value = '';
    inputs.sendBtn.disabled = true;

    // Show typing generic...
    const loadingId = addMessageToChat('bot', 'Thinking...');

    try {
        const resp = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                selected_class: state.selectedClass,
                subject: state.selectedSubject,
                question: text
            })
        });
        const data = await resp.json();
        const answer = data.answer || "Sorry, I couldn't find an answer.";

        // Remove loading message
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        // Add bot answer
        addMessageToChat('bot', answer);

        // History is saved on server side now.

    } catch (e) {
        console.error(e);
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.textContent = "Error connecting to server.";
    } finally {
        inputs.sendBtn.disabled = false;
    }
}

function addMessageToChat(role, text) {
    const id = 'msg-' + Date.now() + Math.random().toString(36).substr(2, 9);
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.id = id;

    div.innerHTML = `
        <div class="avatar ${role}-avatar">${role === 'user' ? 'U' : 'AI'}</div>
        <div class="message-content">${formatText(text)}</div>
    `;

    containers.chatMessages.appendChild(div);
    containers.chatMessages.scrollTop = containers.chatMessages.scrollHeight;
    return id;
}

/* Profile Logic */
function initProfile() {
    renderProfile(); // Initial render

    const saveBtn = document.getElementById('profile-save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            const nameInput = document.getElementById('profile-input-name');
            const emailInput = document.getElementById('profile-input-email');

            if (nameInput && emailInput) {
                const newName = nameInput.value.trim();
                const newEmail = emailInput.value.trim();

                if (newName) {
                    // Calculate initials
                    const words = newName.split(' ');
                    let initials = '';
                    if (words.length >= 2) {
                        initials = (words[0][0] + words[words.length - 1][0]).toUpperCase();
                    } else if (words.length === 1) {
                        initials = words[0].slice(0, 2).toUpperCase();
                    } else {
                        initials = "??";
                    }

                    // Update state
                    state.userProfile = {
                        name: newName,
                        email: newEmail,
                        initials: initials
                    };

                    // Persist
                    localStorage.setItem('eduquest_user_profile', JSON.stringify(state.userProfile));

                    // Update UI
                    renderProfile();
                    alert("Profile updated successfully!");
                }
            }
        });
    }
}

function renderProfile() {
    const avatarEl = document.getElementById('profile-items-avatar');
    const nameEl = document.getElementById('profile-items-name');
    const inputName = document.getElementById('profile-input-name');
    const inputEmail = document.getElementById('profile-input-email');

    if (avatarEl) avatarEl.textContent = state.userProfile.initials;
    if (nameEl) nameEl.textContent = state.userProfile.name;

    // Also update inputs to match state if we want strict sync, 
    // but usually inputs assume their own state until saved.
    // However, on first load we definitely want state.
    if (inputName && inputName.value !== state.userProfile.name) {
        inputName.value = state.userProfile.name;
    }
    if (inputEmail && inputEmail.value !== state.userProfile.email) {
        inputEmail.value = state.userProfile.email;
    }
}


/* Helpers */
function formatSubject(sub) {
    if (!sub) return '';
    return sub.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function formatText(text) {
    // Simple formatting: newlines to br
    return text.replace(/\n/g, '<br>');
}
