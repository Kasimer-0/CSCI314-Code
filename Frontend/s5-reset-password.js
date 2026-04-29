// Auth flow — Reset Password (paired with US #1 login).
// Two states share the same page: State A captures the email and validates it against
// usersData; State B confirms the link was "sent" and offers a resend action.

const stateRequest = document.getElementById('stateRequest');
const stateSent = document.getElementById('stateSent');

const resetForm = document.getElementById('resetForm');
const resetEmailInput = document.getElementById('resetEmail');
const sendResetBtn = document.getElementById('sendResetBtn');
const errorBox = document.getElementById('errorBox');
const sentToEmail = document.getElementById('sentToEmail');
const resendBtn = document.getElementById('resendBtn');
const resendNote = document.getElementById('resendNote');

let resendCooldown = false;

function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove('hidden');
}

function hideError() {
    errorBox.classList.add('hidden');
}

function transitionToSentState(email) {
    sentToEmail.textContent = email;
    stateRequest.classList.add('hidden');
    stateSent.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

resetForm.addEventListener('submit', (e) => {
    e.preventDefault();
    hideError();

    const email = resetEmailInput.value.trim().toLowerCase();
    if (!email) {
        showError('Enter the email associated with your account.');
        return;
    }
    if (!email.includes('@')) {
        showError('That email address does not look right.');
        return;
    }

    // Always confirm — never reveal whether an email exists (avoids account enumeration).
    sendResetBtn.disabled = true;
    sendResetBtn.textContent = 'Sending…';
    setTimeout(() => transitionToSentState(email), 500);
});

resendBtn.addEventListener('click', () => {
    if (resendCooldown) return;
    resendCooldown = true;
    resendBtn.disabled = true;
    resendNote.textContent = 'Reset link resent. You can request another in 30 seconds.';
    resendNote.classList.remove('hidden');
    setTimeout(() => {
        resendCooldown = false;
        resendBtn.disabled = false;
        resendNote.classList.add('hidden');
    }, 30000);
});
