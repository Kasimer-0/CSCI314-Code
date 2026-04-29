// US #4 + #5 — View User Account / Profile.
// Reads ?userId from the URL and renders read-only profile detail. The "Edit Profile" button
// links to uc58.html for the same user. Donee/Fundraiser users get the donations/
// saved/active stat strip; admins get a permissions card.

const params = new URLSearchParams(window.location.search);
const userId = parseInt(params.get('userId'), 10);

const errorBox = document.getElementById('errorBox');
const profileBody = document.getElementById('profileBody');
const editLink = document.getElementById('editLink');

function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove('hidden');
    profileBody.classList.add('hidden');
    editLink.classList.add('opacity-50', 'pointer-events-none');
}

if (!userId) {
    showError('No user selected. Open a user from the User Management table.');
} else {
    const user = usersData.find(u => u.user_id === userId);
    if (!user) {
        showError(`No user found with ID ${userId}.`);
    } else {
        renderUser(user);
    }
}

function renderUser(user) {
    document.getElementById('crumbName').textContent = user.username;
    document.getElementById('pageTitle').textContent = user.username + "'s Profile";
    document.getElementById('pageSubtitle').textContent = `Manage personal information and account settings for ${user.username}`;

    editLink.href = `uc58.html?userId=${user.user_id}`;

    document.getElementById('avatarLg').textContent = window.FS.initials(user.username);
    document.getElementById('userFullName').textContent = user.username;
    document.getElementById('userEmailDisplay').textContent = user.email;

    // Status pill
    const pill = document.getElementById('statusPill');
    const verifiedTag = user.email_verified
        ? ` · Verified ${user.role_name}`
        : '';
    if (user.status === 'Active') {
        pill.className = 'mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700';
        pill.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>Active${verifiedTag}`;
    } else if (user.status === 'Suspended') {
        pill.className = 'mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-700';
        pill.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>Suspended`;
    } else if (user.status === 'Pending') {
        pill.className = 'mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700';
        pill.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Pending invite`;
    } else {
        pill.className = 'mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700';
        pill.textContent = user.status;
    }

    // Stats strip (Donee/Fundraiser show activity stats; Admins show permission count)
    const stats = document.getElementById('statsGrid');
    if (window.FS.isAdminRole(user.role_name) || user.role_name === 'Platform Manager') {
        const permCount = (user.permissions || []).length;
        stats.innerHTML = `
            <div><p class="text-2xl font-bold text-slate-900">${permCount}</p><p class="text-xs text-slate-500">Permissions</p></div>
            <div><p class="text-2xl font-bold text-slate-900">${user.department ? '1' : '0'}</p><p class="text-xs text-slate-500">Team</p></div>
            <div><p class="text-2xl font-bold text-slate-900">${user.two_factor ? 'On' : 'Off'}</p><p class="text-xs text-slate-500">2FA</p></div>`;
    } else {
        const s = user.stats || { donations: 0, saved: 0, active: 0 };
        stats.innerHTML = `
            <div><p class="text-2xl font-bold text-slate-900">${s.donations}</p><p class="text-xs text-slate-500">Donations</p></div>
            <div><p class="text-2xl font-bold text-slate-900">${s.saved}</p><p class="text-xs text-slate-500">Saved</p></div>
            <div><p class="text-2xl font-bold text-slate-900">${s.active}</p><p class="text-xs text-slate-500">Active</p></div>`;
    }

    // Personal information
    document.getElementById('fldFullName').textContent = user.username;
    document.getElementById('fldEmail').textContent = user.email;
    document.getElementById('fldPhone').textContent = user.phone || '—';
    document.getElementById('fldDob').textContent = window.FS.formatDateLong(user.date_of_birth);
    document.getElementById('fldLocation').textContent = user.location || '—';

    const roleStyles = {
        'Donee':            'bg-violet-100 text-violet-700',
        'Fundraiser':       'bg-amber-100 text-amber-700',
        'User Admin':       'bg-blue-100 text-blue-700',
        'Platform Admin':   'bg-indigo-100 text-indigo-700',
        'Super Admin':      'bg-rose-100 text-rose-700',
        'Platform Manager': 'bg-yellow-100 text-yellow-800'
    };
    document.getElementById('fldRole').innerHTML =
        `<span class="inline-flex px-2.5 py-1 rounded-full text-[11px] font-bold ${roleStyles[user.role_name] || 'bg-slate-100 text-slate-700'}">${user.role_name}</span>`;

    // Account & security
    document.getElementById('fldMemberSince').textContent = window.FS.formatDateLong(user.member_since);
    document.getElementById('fldLastSignin').textContent = user.last_signin || '—';

    const fld2fa = document.getElementById('fld2fa');
    if (user.two_factor) {
        fld2fa.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-700"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>Enabled</span>`;
    } else {
        fld2fa.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-700"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Not enabled</span> <a href="#" class="text-xs text-blue-600 font-semibold hover:underline">Enable now</a>`;
    }

    const fldEv = document.getElementById('fldEmailVerified');
    if (user.email_verified) {
        fldEv.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-700"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>Verified</span>`;
    } else {
        fldEv.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-700"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Pending verification</span>`;
    }

    // Admin-only permissions card
    if ((user.permissions || []).length) {
        const card = document.getElementById('permsCard');
        card.classList.remove('hidden');
        document.getElementById('permsList').innerHTML = user.permissions.map(p =>
            `<li class="flex items-center gap-2"><span class="text-emerald-600">✓</span><span class="text-slate-700">${window.FS.PERMISSION_LABELS[p] || p}</span></li>`
        ).join('');
    }

    // Top-right avatar reflects the viewing admin (from session if present, otherwise this user)
    let viewer = null;
    try {
        const raw = localStorage.getItem('fs.session') || sessionStorage.getItem('fs.session');
        if (raw) viewer = JSON.parse(raw);
    } catch (_) { /* noop */ }
    const navBtn = document.getElementById('logoutTrigger');
    if (navBtn) navBtn.textContent = window.FS.initials(viewer ? viewer.username : user.username);
}
