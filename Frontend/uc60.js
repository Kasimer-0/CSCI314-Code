// ====== DOM Elements ======
const tableBody = document.getElementById('tableBody');
const pendingCount = document.getElementById('pendingCount');

// Modal Elements
const reviewModal = document.getElementById('reviewModal');
const modalError = document.getElementById('modalError');
const reviewUserId = document.getElementById('reviewUserId');
const reviewName = document.getElementById('reviewName');
const reviewEmail = document.getElementById('reviewEmail');
const assignRole = document.getElementById('assignRole');

// Buttons
const rejectBtn = document.getElementById('rejectBtn');
const cancelBtn = document.getElementById('cancelBtn');
const approveBtn = document.getElementById('approveBtn');
const toastSuccess = document.getElementById('toastSuccess');
const toastMsg = document.getElementById('toastMsg');


// ====== Normal Flow 2: Displays pending requests ======
function renderPendingTable() {
    tableBody.innerHTML = '';
    
    // STRICTLY filter only 'Pending' users
    const pendingUsers = usersData.filter(user => user.status === 'Pending');
    
    // Update counter badge
    pendingCount.textContent = `${pendingUsers.length} Pending`;

    if (pendingUsers.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="3" class="px-6 py-16 text-center">
                    <div class="flex flex-col items-center justify-center">
                        <svg class="w-12 h-12 text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <p class="text-slate-500 text-sm font-medium">All caught up! No pending registration requests.</p>
                    </div>
                </td>
            </tr>`;
        return;
    }

    pendingUsers.forEach(user => {
        const row = `
            <tr class="hover:bg-slate-50 transition duration-150">
                <td class="px-6 py-4">
                    <div class="flex items-center">
                        <div class="h-10 w-10 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center font-bold border border-amber-200">
                            ${user.username.charAt(0).toUpperCase()}
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-bold text-slate-900">${user.username}</div>
                            <div class="text-sm text-slate-500">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4">
                    <span class="text-sm font-medium text-slate-600">${user.role_name}</span>
                    <span class="text-[10px] uppercase tracking-wider text-slate-400 ml-1">(Requested)</span>
                </td>
                <td class="px-6 py-4 text-right">
                    <!-- Normal Flow 3 Trigger: Select a request -->
                    <button onclick="openReviewModal(${user.user_id})" class="bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 hover:text-blue-600 px-4 py-2 rounded-lg text-sm font-semibold shadow-sm transition">Review</button>
                </td>
            </tr>
        `;
        tableBody.innerHTML += row;
    });
}


// ====== Normal Flow 3: Review Applicant Info ======
function openReviewModal(userId) {
    const user = usersData.find(u => u.user_id === userId);
    if (user) {
        reviewUserId.value = user.user_id;
        reviewName.textContent = user.username;    // Read-only display
        reviewEmail.textContent = user.email;      // Read-only display
        
        // Auto-select their requested role, but force Admin to confirm it
        assignRole.value = user.role_name; 
        
        modalError.classList.add('hidden');
        reviewModal.classList.remove('hidden');
    }
}


// ====== Sub Flow 1: Keep request as pending ======
cancelBtn.addEventListener('click', () => {
    reviewModal.classList.add('hidden');
});


// ====== Normal Flow 5 & 6: Approve and Assign Role ======
approveBtn.addEventListener('click', () => {
    const id = parseInt(reviewUserId.value);
    const selectedRole = assignRole.value;

    // Alternative Flow 3: Error if role not selected
    if (!selectedRole) {
        modalError.textContent = "Action Required: You must explicitly assign a system role before approving.";
        modalError.classList.remove('hidden');
        return;
    }

    // Normal Flow 6: Updates status and role
    const userIndex = usersData.findIndex(u => u.user_id === id);
    if (userIndex !== -1) {
        usersData[userIndex].role_name = selectedRole;
        usersData[userIndex].status = 'Active'; // Activate account
    }

    closeAndShowToast("Success: User account approved and activated.");
});


// ====== Alternative Flow 1 & 2: Reject Application ======
rejectBtn.addEventListener('click', () => {
    const id = parseInt(reviewUserId.value);
    
    // Alternative Flow 2: Update status to rejected
    const userIndex = usersData.findIndex(u => u.user_id === id);
    if (userIndex !== -1) {
        // Here we change the status to 'Suspended' or 'Rejected' (adding 'Rejected' to our vocabulary)
        usersData[userIndex].status = 'Rejected'; 
    }

    closeAndShowToast("Application rejected successfully.");
});


// ====== Utility: Handle Success Flow ======
function closeAndShowToast(message) {
    reviewModal.classList.add('hidden');
    renderPendingTable(); // Refresh the list (approved/rejected users disappear)

    toastMsg.textContent = message;
    toastSuccess.classList.remove('hidden');
    
    // Auto-hide toast
    setTimeout(() => {
        toastSuccess.classList.add('hidden');
    }, 4000);
}

// Initialize page
renderPendingTable();