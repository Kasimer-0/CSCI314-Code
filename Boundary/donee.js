const API = 'http://127.0.0.1:8000/donee';
let token = localStorage.getItem('doneeToken') || null;
let currentTab = 'discover'; 
let currentActivityId = null;

// Security check
if (!token) {
    window.location.href = 'index.html';
} else {
    showDashboard();
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


// ==========================================
// --- Core Business Logic (Auth & Navigation) ---
// ==========================================

// --- LOGOUT DONEE (Story 30) ---
async function logout() {
    showConfirm("Confirm Logout", "Are you sure you want to log out of your Donee account?", async () => {
        try {
            await fetch(`${API}/logout`, { method: 'POST', headers: getHeaders() });
        } catch (e) {
            console.log("Logged out locally.");
        } finally {
            localStorage.removeItem('doneeToken');
            window.location.href = 'index.html';
        }
    });
}

function showDashboard() {
    switchTab('discover');
}

// --- TAB SWITCHING ---
function switchTab(tab) {
    currentTab = tab;
    document.getElementById('searchInput').value = ''; 
    
    const activeClass = "text-left px-4 py-3 rounded-xl bg-emerald-50 text-emerald-700 font-bold transition-all";
    const inactiveClass = "text-left px-4 py-3 rounded-xl hover:bg-slate-50 text-slate-500 font-semibold transition-all";
    
    document.getElementById('nav-discover').className = tab === 'discover' ? activeClass : inactiveClass;
    document.getElementById('nav-favorites').className = tab === 'favorites' ? activeClass : inactiveClass;
    document.getElementById('nav-donations').className = tab === 'donations' ? activeClass : inactiveClass;

    document.getElementById('section-activities').style.display = (tab === 'discover' || tab === 'favorites') ? 'grid' : 'none';
    document.getElementById('section-donations').style.display = tab === 'donations' ? 'block' : 'none';
    
    if(tab === 'discover') { document.getElementById('pageTitle').innerText = "🌍 Discover Activities"; loadActivities(); }
    if(tab === 'favorites') { document.getElementById('pageTitle').innerText = "❤️ My Favorites"; loadFavorites(); }
    if(tab === 'donations') { document.getElementById('pageTitle').innerText = "📜 Donation History"; loadDonations(); }
}

// --- SEARCH TRIGGER (Story 24 & Story 28) ---
function executeSearch() {
    const query = document.getElementById('searchInput').value;
    if(currentTab === 'discover') loadActivities(query);
    if(currentTab === 'favorites') loadFavorites(query);
}

// ==========================================
// --- ACTIVITIES & FAVORITES ---
// ==========================================

// --- SEARCH ONGOING ACTIVITIES (Story 24) ---
async function loadActivities(query = '') {
    const res = await fetch(`${API}/activities${query ? '?title='+query : ''}`, { headers: getHeaders() });
    if(res.status === 401 || res.status === 403) window.location.href = 'index.html';
    const data = await res.json();
    renderActivityCards(data, false);
}

// --- SEARCH MY FAVORITES (Story 28) ---
async function loadFavorites(query = '') {
    const res = await fetch(`${API}/favorites${query ? '?title='+query : ''}`, { headers: getHeaders() });
    const favorites = await res.json();
    const activities = favorites.map(f => f.activity).filter(a => a != null);
    renderActivityCards(activities, true);
}

// Render UI Utility
function renderActivityCards(activities, isFavoriteView) {
    document.getElementById('section-activities').innerHTML = activities.map(a => {
        const progress = Math.min((a.current_amount / a.target_amount) * 100, 100);
        return `
        <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-xl transition-all group flex flex-col h-full">
            <div class="flex justify-between items-start mb-4">
                <span class="${a.status === 'Ongoing' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'} text-[10px] font-black px-2 py-1 rounded tracking-widest uppercase">
                    ${a.status || 'Unknown'}
                </span>
                ${isFavoriteView ? `<button onclick="event.stopPropagation(); removeFavorite(${a.activity_id})" class="text-rose-500 text-xl hover:scale-125 transition-transform" title="Remove from Favorites">❤️</button>` : ''}
            </div>
            <div class="cursor-pointer flex-1" onclick="openModal(${a.activity_id})">
                <h3 class="font-black text-xl text-slate-800 mb-2 group-hover:text-emerald-600 transition-colors line-clamp-2">${a.title}</h3>
                <p class="text-sm text-slate-500 line-clamp-2 mb-6 flex-1">${a.description}</p>
            </div>
            <div class="mt-auto">
                <div class="flex justify-between text-xs font-bold text-slate-800 mb-2">
                    <span class="text-emerald-600">$${a.current_amount.toFixed(2)} raised</span>
                    <span class="text-slate-400">Goal: $${a.target_amount.toFixed(2)}</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-1.5">
                    <div class="bg-emerald-500 h-1.5 rounded-full" style="width: ${progress}%"></div>
                </div>
            </div>
        </div>
    `}).join('') || `<div class="col-span-full text-center py-20 text-slate-400 font-bold text-lg">No activities found.</div>`;
}

// ==========================================
// --- MODAL & DONATION LOGIC ---
// ==========================================

// --- VIEW ACTIVITY DETAILS (Story 25) ---
async function openModal(id) {
    currentActivityId = id;
    const res = await fetch(`${API}/activities/${id}`, { headers: getHeaders() });
    if (!res.ok) {
        const errorData = await res.json();
        showMessage("Unable to view activity", errorData.detail || "The activity is not available or has ended.", true);
        return; // Terminate subsequent operations
    }
    
    const a = await res.json();
    
    document.getElementById('modalTitle').innerText = a.title;
    document.getElementById('modalDesc').innerText = a.description;
    document.getElementById('modalCurrent').innerText = a.current_amount.toFixed(2);
    document.getElementById('modalTarget').innerText = a.target_amount.toFixed(2);
    
    const progress = Math.min((a.current_amount / a.target_amount) * 100, 100);
    setTimeout(() => { document.getElementById('modalProgress').style.width = `${progress}%`; }, 100);

    document.getElementById('donateAmount').value = '';
    document.getElementById('donateMessage').value = '';
    document.getElementById('donateAnon').checked = false;
    document.getElementById('donateModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('donateModal').classList.add('hidden');
    document.getElementById('modalProgress').style.width = '0%';
}

// --- ADD/REMOVE FROM FAVORITES (Story 27) ---
async function toggleFavoriteFromModal() {
    const res = await fetch(`${API}/favorites/${currentActivityId}`, { method: 'POST', headers: getHeaders() });
    const data = await res.json();
    
    // Instead of alert, use custom message modal
    showMessage("Favorites Updated", data.message);
    
    if(currentTab === 'favorites') loadFavorites();
}

// --- REMOVE FROM FAVORITES (Quick remove from Favorites view) ---
async function removeFavorite(activityId) {
    showConfirm("Remove Favorite", "Are you sure you want to remove this from your favorites?", async () => {
        const res = await fetch(`${API}/favorites/${activityId}`, { method: 'POST', headers: getHeaders() });
        const data = await res.json();
        
        showMessage("Removed", data.message);
        if(currentTab === 'favorites') loadFavorites();
    });
}

// --- MAKE A DONATION (Story 31) ---
async function submitDonation() {
    const amount = parseFloat(document.getElementById('donateAmount').value);
    const message = document.getElementById('donateMessage').value;
    const anonymous = document.getElementById('donateAnon').checked;

    if(!amount || amount <= 0) {
        return showMessage("Invalid Amount", "Please enter a valid donation amount greater than 0.", true);
    }

    const res = await fetch(`${API}/activities/${currentActivityId}/donate`, {
        method: 'POST', headers: getHeaders(),
        body: JSON.stringify({ amount, message: message || null, anonymous })
    });

    const data = await res.json();
    if(res.ok) {
        showMessage("Donation Successful!", `Thank you! You successfully donated $${amount.toFixed(2)} to this cause.`);
        closeModal();
        if(currentTab === 'discover') loadActivities();
        if(currentTab === 'favorites') loadFavorites();
    } else {
        showMessage("Donation Failed", data.detail || "An error occurred.", true);
    }
}

// ==========================================
// --- DONATION HISTORY ---
// ==========================================

async function loadDonations() {
    const res = await fetch(`${API}/donations`, { headers: getHeaders() });
    const donations = await res.json();
    
    document.getElementById('donationsList').innerHTML = donations.map(d => `
        <tr class="hover:bg-slate-50 transition-colors">
            <td class="p-5 font-mono text-sm text-slate-500">#${d.donation_id}</td>
            <td class="p-5 font-bold text-slate-800">${d.activity_title}</td>
            <td class="p-5 font-black text-emerald-600">$${d.amount.toFixed(2)}</td>
            <td class="p-5 text-sm text-slate-500">${d.created_at.split('T')[0]}</td>
            <td class="p-5 text-right">
                <button onclick="viewDonationDetail(${d.donation_id})" class="text-xs font-bold bg-white border border-slate-200 text-slate-600 px-4 py-2 rounded-xl hover:bg-slate-100 transition-colors shadow-sm">Receipt</button>
            </td>
        </tr>
    `).join('') || `<tr><td colspan="5" class="text-center py-10 text-slate-400 font-bold">No past donations found.</td></tr>`;
}

// --- VIEW DONATION RECORD DETAIL (Story 32) ---
async function viewDonationDetail(id) {
    const res = await fetch(`${API}/donations/${id}`, { headers: getHeaders() });
    const d = await res.json();
    
    // Populate Custom Receipt Modal instead of alert()
    document.getElementById('receiptId').innerText = `#${d.donation_id}`;
    document.getElementById('receiptActivity').innerText = d.activity_title;
    document.getElementById('receiptDate').innerText = d.created_at.replace('T', ' ').substring(0, 19);
    document.getElementById('receiptAnon').innerText = d.is_anonymous ? 'Yes' : 'No';
    document.getElementById('receiptMessage').innerText = d.message ? `"${d.message}"` : '- None -';
    document.getElementById('receiptAmount').innerText = `$${d.amount.toFixed(2)}`;
    
    document.getElementById('receiptModal').classList.remove('hidden');
}

function closeReceipt() {
    document.getElementById('receiptModal').classList.add('hidden');
}