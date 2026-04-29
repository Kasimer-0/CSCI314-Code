// US #1 — User Admin Log In.
// Looks up the entered email in usersData, blocks Suspended/Pending accounts, and lands the
// authenticated session on the user-management screen (s7).

const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const rememberCheckbox = document.getElementById('rememberMe');
const signInBtn = document.getElementById('signInBtn');
const googleBtn = document.getElementById('googleBtn');
const errorBox = document.getElementById('errorBox');
const errorText = document.getElementById('errorText');

function showError(message) {
    errorText.textContent = message;
    errorBox.classList.remove('hidden');
}

function hideError() {
    errorBox.classList.add('hidden');
}

function persistSession(user, remember) {
    const session = {
        userId: user.user_id,
        username: user.username,
        role: user.role_name,
        signedInAt: new Date().toISOString()
    };
    const store = remember ? localStorage : sessionStorage;
    store.setItem('fs.session', JSON.stringify(session));
}

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    hideError();

    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;

    if (!email || !password) {
        showError('Enter both your email and password to continue.');
        return;
    }
    if (!email.includes('@')) {
        showError('That email address does not look right.');
        return;
    }

    const user = usersData.find(u => u.email.toLowerCase() === email);
    if (!user) {
        showError('We could not find an account with that email.');
        return;
    }
    if (user.status === 'Suspended') {
        showError('This account has been suspended. Contact support to appeal.');
        return;
    }
    if (user.status === 'Pending') {
        showError('This account is pending approval. Check your email for an invite link.');
        return;
    }
    if (user.status === 'Rejected') {
        showError('This registration was rejected and cannot be used to sign in.');
        return;
    }

    // Mock password check — the demo accepts anything non-empty for seeded users.
    persistSession(user, rememberCheckbox.checked);

    signInBtn.disabled = true;
    signInBtn.textContent = 'Signing in…';
    setTimeout(() => {
        // User Admins / Platform Admins / Super Admins → admin dashboard.
        // Everyone else lands on their own profile.
        if (window.FS.isAdminRole(user.role_name)) {
            window.location.href = 'index-UC57.html';
        } else {
            window.location.href = `s3-view-profile.html?userId=${user.user_id}`;
        }
    }, 400);
});

googleBtn.addEventListener('click', () => {
    showError('Single sign-on with Google is not configured in this demo.');
});
