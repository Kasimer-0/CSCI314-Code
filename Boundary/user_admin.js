const API = 'http://127.0.0.1:8000/user-admin';
let token = localStorage.getItem('adminToken') || null;

// Security check
if (!token) {
    window.location.href = 'index.html';
} else {
    loadAccounts();
}

function getHeaders() {
    return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
}

// ==========================================
// --- General UI modal control functions ---
// ==========================================
function showMessage(title, text, isError = false) {
    const icon = document.getElementById('messageIcon');
    icon.innerHTML = isError ? '❌' : '✅';
    icon.className = `w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl ${isError ? 'bg-rose-50 text-rose-500' : 'bg-emerald-50 text-emerald-500'}`;
    document.getElementById('messageTitle').innerText = title;
    document.getElementById('messageText').innerText = text;
    document.getElementById('messageModal').classList.remove('hidden');
}
function closeMessage() { document.getElementById('messageModal').classList.add('hidden'); }

function showConfirm(title, text, onConfirm) {
    document.getElementById('confirmTitle').innerText = title;
    document.getElementById('confirmText').innerText = text;
    document.getElementById('confirmExecuteBtn').onclick = () => { onConfirm(); closeConfirm(); };
    document.getElementById('confirmModal').classList.remove('hidden');
}
function closeConfirm() { document.getElementById('confirmModal').classList.add('hidden'); }

function showPrompt(title, subtitle, initialValue, onSubmit) {
    document.getElementById('promptTitle').innerText = title;
    document.getElementById('promptSubtitle').innerText = subtitle;
    const input = document.getElementById('promptInput');
    input.value = initialValue;
    document.getElementById('promptSubmitBtn').onclick = () => { onSubmit(input.value); closePrompt(); };
    document.getElementById('promptModal').classList.remove('hidden');
    // Delayed focus to prevent animation occlusion
    setTimeout(() => input.focus(), 100); 
}
function closePrompt() { document.getElementById('promptModal').classList.add('hidden'); }
function closeDetail() { document.getElementById('detailModal').classList.add('hidden'); }


// ==========================================
// --- Core Business Logic (Auth & Navigation) ---
// ==========================================

// --- LOGOUT ADMIN (Story 12) ---
async function logout() {
    showConfirm("Confirm Logout", "Are you sure you want to end your admin session?", async () => {
        try {
            await fetch(`${API}/logout`, { method: 'POST', headers: getHeaders() });
        } catch (e) {
            console.log("Logged out locally.");
        } finally {
            localStorage.removeItem('adminToken');
            window.location.href = 'index.html';
        }
    });
}

function switchTab(tab) {
    document.getElementById('section-accounts').style.display = tab === 'accounts' ? 'block' : 'none';
    document.getElementById('section-profiles').style.display = tab === 'profiles' ? 'block' : 'none';
    
    document.getElementById('pageTitle').innerText = tab === 'accounts' ? "User Accounts" : "User Profiles";
    document.getElementById('pageSubtitle').innerText = tab === 'accounts' ? "Manage system access credentials" : "Manage personal details and roles";

    const activeClass = "text-left px-4 py-3 rounded-xl bg-slate-800 text-white font-bold transition-all";
    const inactiveClass = "text-left px-4 py-3 rounded-xl hover:bg-slate-800 text-slate-400 font-semibold transition-all";
    
    document.getElementById('nav-accounts').className = tab === 'accounts' ? activeClass : inactiveClass;
    document.getElementById('nav-profiles').className = tab === 'profiles' ? activeClass : inactiveClass;
    
    if(tab === 'profiles') loadProfiles();
    else loadAccounts();
}

// --- SEARCH ACCOUNTS (Story 10) / SEARCH PROFILES (Story 5) ---
function executeSearch() {
    const q = document.getElementById('searchInput').value;
    if(document.getElementById('section-accounts').style.display !== 'none') loadAccounts(q);
    else loadProfiles(q);
}

// ==========================================
// --- ACCOUNTS (Story 6-10) ---
// ==========================================

// --- SEARCH ACCOUNTS (Story 10) ---
async function loadAccounts(emailQuery = '') {
    const res = await fetch(`${API}/accounts${emailQuery ? '?email='+emailQuery : ''}`, { headers: getHeaders() });
    if(res.status === 401 || res.status === 403) window.location.href = 'index.html';
    const data = await res.json();
    
    document.getElementById('accountsList').innerHTML = data.map(a => `
        <div class="bg-white p-4 rounded-2xl border border-slate-200 flex justify-between items-center hover:shadow-md transition-all">
            <div class="flex items-center gap-4">
                <span class="text-[10px] font-black text-slate-400 bg-slate-100 px-2 py-1 rounded uppercase tracking-widest">ID: ${a.account_id}</span>
                <span class="font-bold text-slate-800">${a.email}</span>
                <span class="text-xs font-bold px-2 py-1 rounded ${a.status === 'Active' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}">${a.status}</span>
            </div>
            <div class="flex gap-2">
                <button onclick="updateAccount(${a.account_id})" class="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-2 rounded-xl hover:bg-blue-100 transition-colors">Update Email</button>
                ${!a.is_suspended ? `<button onclick="suspendAccount(${a.account_id})" class="text-xs font-bold text-rose-600 bg-rose-50 px-3 py-2 rounded-xl hover:bg-rose-100 transition-colors">Suspend</button>` : ''}
            </div>
        </div>
    `).join('');
}

// --- CREATE ACCOUNT (Story 6) ---
async function createAccount() {
    const email = document.getElementById('newAccEmail').value;
    const password = document.getElementById('newAccPass').value;
    
    if (!email || !password) {
        return showMessage("Missing Fields", "Please enter both email and password.", true);
    }

    const res = await fetch(`${API}/accounts`, {
        method: 'POST', headers: getHeaders(), body: JSON.stringify({email, password})
    });
    
    if(res.ok) { 
        showMessage("Success", "Account Created Successfully!"); 
        document.getElementById('newAccEmail').value = '';
        document.getElementById('newAccPass').value = '';
        loadAccounts(); 
    }
    else { 
        const err = await res.json(); 
        showMessage("Failed", err.detail || "An error occurred", true); 
    }
}

// --- UPDATE ACCOUNT (Story 8) ---
async function updateAccount(id) {
    showPrompt("Update Account Email", "Enter the new email address for this user:", "", async (newEmail) => {
        if(!newEmail) return;
        const res = await fetch(`${API}/accounts/${id}?email=${encodeURIComponent(newEmail)}`, { method: 'PATCH', headers: getHeaders() });
        if(res.ok) {
            showMessage("Updated", "Account email has been changed.");
            loadAccounts();
        } else {
            const err = await res.json();
            showMessage("Update Failed", err.detail || "Cannot update email", true);
        }
    });
}

// --- SUSPEND ACCOUNT (Story 9) ---
async function suspendAccount(id) {
    showConfirm("Suspend Account", "This user will be suspended and lose access. Proceed?", async () => {
        await fetch(`${API}/accounts/${id}/suspend`, { method: 'POST', headers: getHeaders() });
        loadAccounts();
    });
}


// ==========================================
// --- PROFILES (Story 1-5) ---
// ==========================================

// --- SEARCH PROFILES (Story 5) ---
async function loadProfiles(nameQuery = '') {
    const res = await fetch(`${API}/profiles${nameQuery ? '?username='+nameQuery : ''}`, { headers: getHeaders() });
    const data = await res.json();
    const roleNames = {0: "Admin", 1: "Donee", 2: "Fundraiser", 3: "Platform Manager"};
    
    document.getElementById('profilesList').innerHTML = data.map(p => `
        <div class="bg-white p-5 rounded-3xl border border-slate-200 hover:border-slate-300 transition-all">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="font-black text-slate-900 text-lg">${p.username}</h3>
                    <p class="text-xs text-slate-400 font-bold uppercase tracking-wider">Profile ID: ${p.profile_id} | Acc: ${p.account_id}</p>
                </div>
                <span class="text-[10px] font-black bg-slate-900 text-white px-2 py-1 rounded uppercase tracking-widest">${roleNames[p.role_id]}</span>
            </div>
            <div class="flex gap-2 pt-4 border-t border-slate-50">
                <button onclick="viewProfile(${p.profile_id})" class="flex-1 text-xs font-bold text-slate-600 bg-slate-100 py-2 rounded-xl hover:bg-slate-200">View</button>
                <button onclick="updateProfile(${p.profile_id}, '${p.username}')" class="flex-1 text-xs font-bold text-blue-600 bg-blue-50 py-2 rounded-xl hover:bg-blue-100">Edit</button>
                <button onclick="suspendProfile(${p.profile_id})" class="flex-1 text-xs font-bold text-rose-600 bg-rose-50 py-2 rounded-xl hover:bg-rose-100">Suspend</button>
            </div>
        </div>
    `).join('');
}

// --- CREATE PROFILE (Story 1) ---
async function createProfile() {
    const account_id = parseInt(document.getElementById('newProfAccId').value);
    const username = document.getElementById('newProfName').value;
    const role_id = parseInt(document.getElementById('newProfRole').value);
    
    if(!account_id || !username) {
        return showMessage("Missing Fields", "Please fill all required profile fields.", true);
    }

    const res = await fetch(`${API}/profiles`, {
        method: 'POST', headers: getHeaders(), body: JSON.stringify({account_id, username, role_id})
    });
    
    if(res.ok) { 
        showMessage("Success", "Profile linked to account successfully!"); 
        document.getElementById('newProfAccId').value = '';
        document.getElementById('newProfName').value = '';
        loadProfiles(); 
    }
    else { 
        const err = await res.json(); 
        showMessage("Failed", err.detail || "Cannot link profile", true); 
    }
}

// --- VIEW PROFILE (Story 2) ---
async function viewProfile(id) {
    const res = await fetch(`${API}/profiles/${id}`, { headers: getHeaders() });
    const p = await res.json();
    const roleNames = {0: "Admin", 1: "Donee", 2: "Fundraiser", 3: "Platform Manager"};
    
    document.getElementById('detailLabel').innerText = roleNames[p.role_id];
    document.getElementById('detailMainTitle').innerText = p.username;
    document.getElementById('detailContent').innerHTML = `
        <div class="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
            <strong class="text-slate-500 text-sm">Account ID</strong> 
            <span class="font-bold">${p.account_id}</span>
        </div>
        <div class="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
            <strong class="text-slate-500 text-sm">Profile ID</strong> 
            <span class="font-bold">${p.profile_id}</span>
        </div>
        <div class="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
            <strong class="text-slate-500 text-sm">Status</strong> 
            <span class="font-bold ${p.status === 'Active' ? 'text-emerald-600' : 'text-rose-600'}">${p.status}</span>
        </div>
    `;
    document.getElementById('detailModal').classList.remove('hidden');
}

// --- UPDATE PROFILE (Story 3) ---
async function updateProfile(id, oldName) {
    showPrompt("Edit Username", "Update the display name for this user:", oldName, async (name) => {
        if(!name) return;
        const res = await fetch(`${API}/profiles/${id}`, { method: 'PATCH', headers: getHeaders(), body: JSON.stringify({username: name}) });
        if(res.ok) {
            showMessage("Updated", "Username has been updated.");
            loadProfiles();
        } else {
            const err = await res.json();
            showMessage("Update Failed", err.detail || "Cannot update username", true);
        }
    });
}

// --- SUSPEND PROFILE (Story 4) ---
async function suspendProfile(id) {
    showConfirm("Suspend Profile", "Are you sure you want to suspend this user profile?", async () => {
        await fetch(`${API}/profiles/${id}/suspend`, { method: 'POST', headers: getHeaders() });
        loadProfiles();
    });
}