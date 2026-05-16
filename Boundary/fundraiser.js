const API = 'http://127.0.0.1:8000/fundraiser';
let token = localStorage.getItem('fundToken') || null;
let currentTab = 'ongoing'; 

// Security check: Force redirection if no token is found.
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

// --- LOGOUT FUNDRAISER (Story 19) ---
function logout() {
    document.getElementById('logoutModal').classList.remove('hidden');
}

function closeLogoutModal() {
    document.getElementById('logoutModal').classList.add('hidden');
}

async function confirmLogout() {
    try {
        await fetch(`${API}/logout`, { method: 'POST', headers: getHeaders() });
    } catch (e) {
        console.log("Session already expired or network error.");
    } finally {
        localStorage.removeItem('fundToken');
        window.location.href = 'index.html'; 
    }
}

function showDashboard() {
    switchTab('ongoing');
}

// --- TAB SWITCHING ---
function switchTab(tab) {
    currentTab = tab;
    document.getElementById('searchInput').value = '';
    
    const activeClass = "text-left px-4 py-3 rounded-xl bg-slate-800 text-amber-400 font-bold transition-all";
    const inactiveClass = "text-left px-4 py-3 rounded-xl hover:bg-slate-800 text-slate-400 font-semibold transition-all";
    
    document.getElementById('nav-ongoing').className = tab === 'ongoing' ? activeClass : inactiveClass;
    document.getElementById('nav-history').className = tab === 'history' ? activeClass : inactiveClass;
    
    document.getElementById('nav-create').className = tab === 'create' ? 
        "text-left px-4 py-3 rounded-xl bg-amber-500 text-white font-bold transition-all flex items-center justify-between" : 
        "text-left px-4 py-3 rounded-xl hover:bg-slate-800 text-slate-400 font-semibold transition-all flex items-center justify-between";

    document.getElementById('section-list').style.display = (tab === 'ongoing' || tab === 'history') ? 'grid' : 'none';
    document.getElementById('section-create').style.display = tab === 'create' ? 'block' : 'none';
    document.getElementById('searchContainer').style.visibility = tab === 'create' ? 'hidden' : 'visible';
    
    // Switch Data Context
    if(tab === 'ongoing') { 
        document.getElementById('pageTitle').innerText = "🚀 Ongoing Campaigns"; 
        document.getElementById('pageSubtitle').innerText = "Manage and track your active fundraising goals.";
        loadActivities(`${API}/activities`, true); 
    }
    if(tab === 'history') { 
        document.getElementById('pageTitle').innerText = "📚 Past History"; 
        document.getElementById('pageSubtitle').innerText = "Review closed or suspended campaigns.";
        loadActivities(`${API}/history`, false); 
    }
    if(tab === 'create') { 
        document.getElementById('pageTitle').innerText = "Launch New Campaign"; 
        document.getElementById('pageSubtitle').innerText = "Fill out the details below to start raising funds.";
    }
}

// --- SEARCH ACTIVITIES (Story 17) & SEARCH HISTORY (Story 22) ---
function executeSearch() {
    const query = document.getElementById('searchInput').value;
    const route = currentTab === 'ongoing' ? 'activities' : 'history';
    loadActivities(`${API}/${route}${query ? '?title='+query : ''}`, currentTab === 'ongoing');
}


// ==========================================
// --- ACTIVITIES MANAGEMENT ---
// ==========================================

// --- VIEW MY ACTIVITIES (Story 14) & SEARCH HISTORY (Story 22) ---
async function loadActivities(url, isOngoing) {
    const res = await fetch(url, { headers: getHeaders() });
    if(res.status === 401 || res.status === 403) window.location.href = 'index.html';
    const activities = await res.json();
    
    document.getElementById('section-list').innerHTML = activities.map(a => {
        const progress = Math.min((a.current_amount / a.target_amount) * 100, 100);
        // Safe escaping of headers to prevent single quotes from breaking HTML attributes
        const safeTitle = a.title.replace(/'/g, "\\'");

        return `
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div>
                <div class="flex justify-between items-center mb-4">
                    <span class="${isOngoing ? 'bg-amber-50 text-amber-600 border border-amber-200/60' : 'bg-slate-100 text-slate-500'} text-[10px] font-black px-2.5 py-1 rounded-md tracking-widest uppercase">
                        ${a.status}
                    </span>
                </div>
                
                <h3 class="font-bold text-xl text-slate-900 mb-2 truncate" title="${a.title}">${a.title}</h3>
                <p class="text-sm text-slate-500 line-clamp-2 mb-6 h-10">${a.description}</p>
                
                <div class="mb-6">
                    <div class="flex justify-between text-xs font-bold text-slate-700 mb-2">
                        <span>$${a.current_amount.toFixed(2)} raised</span>
                        <span class="text-slate-400">Goal: $${a.target_amount.toFixed(2)}</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2">
                        <div class="${isOngoing ? 'bg-amber-500' : 'bg-slate-400'} h-2 rounded-full transition-all duration-500" style="width: ${progress}%"></div>
                    </div>
                </div>
            </div>

            <div class="border-t border-slate-100 pt-4">
                ${isOngoing ? `
                <div class="space-y-2">
                    <div class="flex gap-2">
                        <button onclick="viewOngoingDetail(${a.activity_id})" class="flex-1 text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 py-2.5 rounded-xl hover:bg-slate-100 transition-all active:scale-95">View Details</button>
                        <button onclick="viewStats(${a.activity_id})" class="flex-1 text-xs font-bold text-amber-600 bg-amber-50 border border-amber-100 py-2.5 rounded-xl hover:bg-amber-100 transition-all active:scale-95">Stats dashboard</button>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="updateTitle(${a.activity_id}, '${safeTitle}')" class="flex-1 text-xs font-bold text-blue-600 bg-blue-50/60 py-2 rounded-xl hover:bg-blue-100 transition-colors">Edit Title</button>
                        <button onclick="suspendActivity(${a.activity_id})" class="flex-1 text-xs font-bold text-rose-600 bg-rose-50/60 py-2 rounded-xl hover:bg-rose-100 transition-colors">Suspend</button>
                    </div>
                </div>
                ` : `
                <button onclick="viewPastDetail(${a.activity_id})" class="w-full text-center text-sm font-bold text-slate-500 bg-slate-50 border border-slate-200 py-2.5 rounded-xl hover:bg-slate-200 hover:text-slate-800 transition-all">View Full Archive</button>
                `}
            </div>
        </div>
        `;
    }).join('') || `<div class="col-span-full text-center py-20 text-slate-400 font-bold text-lg">No campaigns found.</div>`;
}

// --- CREATE ACTIVITY (Story 13) ---
async function createActivity() {
    const title = document.getElementById('createTitle').value;
    const description = document.getElementById('createDesc').value;
    const category_id = parseInt(document.getElementById('createCategory').value);
    const target_amount = parseFloat(document.getElementById('createTarget').value);
    const is_private = document.getElementById('createPrivate').checked;

    if(!title || !description || !category_id || !target_amount) {
        return showMessage("Missing Details", "Please fill in all required campaign fields before publishing.", true);
    }

    const res = await fetch(`${API}/activities`, {
        method: 'POST', headers: getHeaders(),
        body: JSON.stringify({ title, description, category_id, target_amount, is_private })
    });

    if(res.ok) {
        showMessage("Campaign Published", "Your new fundraising campaign is now live!");
        switchTab('ongoing');
    } else {
        const data = await res.json();
        showMessage("Publish Failed", data.detail || "An error occurred during publication.", true);
    }
}

// --- VIEW ONGOING ACTIVITY DETAIL (Story 14) ---
async function viewOngoingDetail(id) {
    try {
        // Request the Story 14 API from the backend.
        const res = await fetch(`${API}/activities/${id}`, { headers: getHeaders() });
        const data = await res.json();

        if (res.ok) {
            // Reuse the existing detailModal structure and dynamically populate the data
            document.getElementById('detailTitle').innerText = data.title;
            document.getElementById('detailDesc').innerText = data.description;
            document.getElementById('detailStatus').innerText = data.status;
            document.getElementById('detailCurrent').innerText = `$${data.current_amount.toFixed(2)}`;
            document.getElementById('detailGoal').innerText = `$${data.target_amount.toFixed(2)}`;
            
            const date = new Date(data.created_at);
            document.getElementById('detailDate').innerText = date.toLocaleDateString('en-SG', { 
                year: 'numeric', month: 'long', day: 'numeric' 
            });

            // Calculate progress bar
            const progress = Math.min((data.current_amount / data.target_amount) * 100, 100);
            document.getElementById('detailProgress').style.width = `${progress}%`;

            // Remove hidden class, display the elegant modal
            document.getElementById('detailModal').classList.remove('hidden');
        } else {
            showMessage("Error", data.detail || "Failed to load campaign details.", true);
        }
    } catch (err) {
        showMessage("Connection Error", "Cannot fetch details from server.", true);
    }
}

// --- UPDATE ACTIVITY TITLE (Story 15) ---
function updateTitle(id, currentTitle) {
    document.getElementById('editActivityId').value = id;
    document.getElementById('newTitleInput').value = currentTitle;
    document.getElementById('editTitleModal').classList.remove('hidden');
    setTimeout(() => document.getElementById('newTitleInput').focus(), 100);
}

function closeEditTitle() {
    document.getElementById('editTitleModal').classList.add('hidden');
}

async function submitUpdateTitle() {
    const id = document.getElementById('editActivityId').value;
    const newTitle = document.getElementById('newTitleInput').value;

    if (!newTitle || newTitle.length < 5) {
        return showMessage("Invalid Title", "Title must be at least 5 characters long.", true);
    }

    const res = await fetch(`${API}/activities/${id}?title=${encodeURIComponent(newTitle)}`, { 
        method: 'PATCH', 
        headers: getHeaders() 
    });

    if (res.ok) {
        closeEditTitle();
        executeSearch(); 
    } else {
        const error = await res.json();
        showMessage("Update Failed", error.detail || "Could not save the new title.", true);
    }
}

// --- SUSPEND ACTIVITY (Story 16) ---
async function suspendActivity(id) {
    showConfirm("Suspend Campaign", "Are you sure you want to suspend this activity? It will no longer accept donations.", async () => {
        const res = await fetch(`${API}/activities/${id}/suspend`, { method: 'POST', headers: getHeaders() });
        if(res.ok) {
            executeSearch(); // Refresh list to remove suspended item
        } else {
            const err = await res.json();
            showMessage("Error", err.detail || "Could not suspend campaign.", true);
        }
    });
}

// ==========================================
// --- DATA TRACKING & ARCHIVE ---
// ==========================================

// --- TRACK ACTIVITY VIEWS (Story 20) & TRACK SHORTLISTS (Story 21) ---
async function viewStats(id) {
    try {
        const res = await fetch(`${API}/activities/${id}/stats`, { headers: getHeaders() });
        const data = await res.json();
        
        document.getElementById('statTitle').innerText = data.title;
        document.getElementById('statViews').innerText = data.views || 0;
        document.getElementById('statShortlist').innerText = data.shortlisted_times || 0;
        document.getElementById('statsModal').classList.remove('hidden');
    } catch(e) {
        showMessage("Data Unavailable", "Could not retrieve statistics for this campaign.", true);
    }
}

function closeStats() {
    document.getElementById('statsModal').classList.add('hidden');
}

// --- VIEW PAST ACTIVITY DETAIL (Story 23) ---
async function viewPastDetail(id) {
    const res = await fetch(`${API}/history/${id}`, { headers: getHeaders() });
    const data = await res.json();

    if (res.ok) {
        document.getElementById('detailTitle').innerText = data.title;
        document.getElementById('detailDesc').innerText = data.description;
        document.getElementById('detailStatus').innerText = data.status;
        document.getElementById('detailCurrent').innerText = `$${data.current_amount.toFixed(2)}`;
        document.getElementById('detailGoal').innerText = `$${data.target_amount.toFixed(2)}`;
        
        const date = new Date(data.created_at);
        document.getElementById('detailDate').innerText = date.toLocaleDateString('en-SG', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        });

        const progress = Math.min((data.current_amount / data.target_amount) * 100, 100);
        document.getElementById('detailProgress').style.width = `${progress}%`;

        document.getElementById('detailModal').classList.remove('hidden');
    } else {
        showMessage("Archive Error", data.detail || "Failed to load past archive details.", true);
    }
}

function closeDetail() {
    document.getElementById('detailModal').classList.add('hidden');
}
