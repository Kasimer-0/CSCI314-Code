const API = 'http://127.0.0.1:8000/platform';
let token = localStorage.getItem('pmToken') || null;

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
function closeDetail() { document.getElementById('detailModal').classList.add('hidden'); }


// ==========================================
// --- Core Business Logic (Auth & Navigation) ---
// ==========================================

// --- LOGOUT PLATFORM MANAGER (Story 39) ---
async function logout() {
    showConfirm("Confirm Logout", "Are you sure you want to log out of the Manager Portal?", async () => {
        try {
            await fetch(`${API}/logout`, { method: 'POST', headers: getHeaders() });
        } catch (e) {
            console.log("Logged out locally.");
        } finally {
            localStorage.removeItem('pmToken');
            window.location.href = 'index.html';
        }
    });
}

function showDashboard() {
    switchTab('categories');
}

function switchTab(tab) {
    document.getElementById('section-categories').style.display = tab === 'categories' ? 'block' : 'none';
    document.getElementById('section-reports').style.display = tab === 'reports' ? 'block' : 'none';
    document.getElementById('searchContainer').style.visibility = tab === 'reports' ? 'hidden' : 'visible';
    
    document.getElementById('pageTitle').innerText = tab === 'categories' ? "Category Management" : "Data Reports";
    document.getElementById('pageSubtitle').innerText = tab === 'categories' ? "Organize fundraising activities globally" : "Generate macro-level insights";

    const activeClass = "text-left px-4 py-3 rounded-xl bg-slate-800 text-violet-400 font-bold transition-all";
    const inactiveClass = "text-left px-4 py-3 rounded-xl hover:bg-slate-800 text-slate-400 font-semibold transition-all";
    
    document.getElementById('nav-categories').className = tab === 'categories' ? activeClass : inactiveClass;
    document.getElementById('nav-reports').className = tab === 'reports' ? activeClass : inactiveClass;
    
    if(tab === 'categories') loadCategories();
}

// --- SEARCH CATEGORIES TRIGGER (Story 37) ---
function executeSearch() {
    const q = document.getElementById('searchInput').value;
    loadCategories(q);
}

// ==========================================
// --- CATEGORIES MANAGEMENT (Story 33-37) ---
// ==========================================

// --- SEARCH & LIST CATEGORIES (Story 37) ---
async function loadCategories(nameQuery = '') {
    const res = await fetch(`${API}/categories${nameQuery ? '?name='+nameQuery : ''}`, { headers: getHeaders() });
    if(res.status === 401 || res.status === 403) window.location.href = 'index.html';
    const categories = await res.json();
    
    document.getElementById('categoryList').innerHTML = categories.map(c => `
        <div class="bg-white p-6 rounded-3xl border border-slate-200 hover:border-violet-300 transition-all shadow-sm">
            <div class="flex justify-between items-start mb-2">
                <span class="text-[10px] font-black text-slate-400 bg-slate-100 px-2 py-1 rounded tracking-widest uppercase">ID: ${c.category_id}</span>
                <span class="text-xs font-bold px-2 py-1 rounded ${c.is_archived ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}">${c.is_archived ? 'Suspended' : 'Active'}</span>
            </div>
            <h3 class="font-bold text-xl text-slate-900 mb-1">${c.name}</h3>
            <p class="text-sm text-slate-500 mb-6 truncate">${c.description || 'No description'}</p>
            <div class="flex gap-2 border-t border-slate-50 pt-4">
                <button onclick="viewCategory(${c.category_id})" class="flex-1 text-xs font-bold text-indigo-600 bg-indigo-50 py-2 rounded-xl hover:bg-indigo-100">View</button>
                ${!c.is_archived ? `
                <button onclick="openEditCategory(${c.category_id}, '${c.name.replace(/'/g, "\\'")}', '${(c.description || '').replace(/'/g, "\\'")}')" class="flex-1 text-xs font-bold text-slate-700 bg-slate-100 py-2 rounded-xl hover:bg-slate-200">Edit</button>
                <button onclick="suspendCategory(${c.category_id})" class="flex-1 text-xs font-bold text-rose-600 bg-rose-50 py-2 rounded-xl hover:bg-rose-100">Suspend</button>
                ` : ''}
            </div>
        </div>
    `).join('') || `<div class="col-span-full text-center py-10 text-slate-400 font-bold">No categories found.</div>`;
}

// --- CREATE CATEGORY (Story 33) ---
async function createCategory() {
    const name = document.getElementById('createCatName').value;
    const description = document.getElementById('createCatDesc').value;
    
    if(!name) return showMessage("Input Required", "Category Name is required.", true);
    
    const res = await fetch(`${API}/categories`, {
        method: 'POST', headers: getHeaders(), body: JSON.stringify({ name, description })
    });
    
    if(res.ok) { 
        document.getElementById('createCatName').value = ''; 
        document.getElementById('createCatDesc').value = ''; 
        showMessage("Success", "Category created successfully.");
        loadCategories(); 
    }
    else {
        const err = await res.json();
        showMessage("Creation Failed", err.detail || "Failed to create category.", true);
    }
}

// --- VIEW CATEGORY (Story 34) ---
async function viewCategory(id) {
    const res = await fetch(`${API}/categories/${id}`, { headers: getHeaders() });
    const c = await res.json();
    
    document.getElementById('detailMainTitle').innerText = c.name;
    document.getElementById('detailContent').innerHTML = `
        <div class="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
            <strong class="text-slate-500 text-sm">Category ID</strong> 
            <span class="font-bold">${c.category_id}</span>
        </div>
        <div class="flex justify-between items-start py-2 border-b border-slate-100 last:border-0">
            <strong class="text-slate-500 text-sm">Description</strong> 
            <span class="text-right text-sm text-slate-600 pl-4">${c.description || 'N/A'}</span>
        </div>
        <div class="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
            <strong class="text-slate-500 text-sm">Status</strong> 
            <span class="font-bold ${c.is_archived ? 'text-rose-600' : 'text-emerald-600'}">${c.is_archived ? 'Suspended' : 'Active'}</span>
        </div>
    `;
    document.getElementById('detailModal').classList.remove('hidden');
}

// --- UPDATE CATEGORY (Story 35) ---
function openEditCategory(id, currentName, currentDesc) {
    document.getElementById('editCatId').value = id;
    document.getElementById('editCatName').value = currentName;
    document.getElementById('editCatDesc').value = currentDesc;
    document.getElementById('editCategoryModal').classList.remove('hidden');
    setTimeout(() => document.getElementById('editCatName').focus(), 100);
}

function closeEditCategory() {
    document.getElementById('editCategoryModal').classList.add('hidden');
}

async function submitUpdateCategory() {
    const id = document.getElementById('editCatId').value;
    const name = document.getElementById('editCatName').value;
    const desc = document.getElementById('editCatDesc').value;

    if(!name) {
        return showMessage("Input Required", "Category Name cannot be empty.", true);
    }

    const res = await fetch(`${API}/categories/${id}`, {
        method: 'PATCH', headers: getHeaders(), body: JSON.stringify({ name, description: desc })
    });

    if(res.ok) {
        closeEditCategory();
        showMessage("Updated", "Category has been updated successfully.");
        loadCategories();
    } else {
        const err = await res.json();
        showMessage("Update Failed", err.detail || "Could not update category.", true);
    }
}

// --- SUSPEND CATEGORY (Story 36) ---
async function suspendCategory(id) {
    showConfirm("Suspend Category", "Are you sure you want to suspend this category? It will no longer be available for new campaigns.", async () => {
        await fetch(`${API}/categories/${id}/suspend`, { method: 'POST', headers: getHeaders() });
        loadCategories();
    });
}

// ==========================================
// --- PLATFORM REPORTS (Story 40-42) ---
// ==========================================

async function generateReport(type) {
    const res = await fetch(`${API}/reports/${type}`, { headers: getHeaders() });
    
    if(res.ok) {
        const result = await res.json();
        document.getElementById('reportCanvas').classList.remove('hidden');
        document.getElementById('repTypeLabel').innerText = result.report_type;
        document.getElementById('repCamps').innerText = result.data.new_activities_launched;
        document.getElementById('repTrans').innerText = result.data.transactions_count;
        document.getElementById('repFunds').innerText = "$" + parseFloat(result.data.total_donations_amount).toLocaleString(undefined, {minimumFractionDigits: 2});
        document.getElementById('repDate').innerText = `Period: ${result.data.period_start.split('T')[0]} to ${result.data.period_end.split('T')[0]}`;
    } else {
        showMessage("Report Error", "Failed to generate system report.", true);
    }
}