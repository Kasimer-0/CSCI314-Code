// ====== DOM Elements ======
const logsTableBody = document.getElementById('logsTableBody');
const logSearchInput = document.getElementById('logSearchInput');
const actionFilter = document.getElementById('actionFilter');
const dateFilter = document.getElementById('dateFilter');
const searchLogsBtn = document.getElementById('searchLogsBtn');
const clearLogsBtn = document.getElementById('clearLogsBtn');
const systemMsgBox = document.getElementById('systemMsgBox');

// ====== Render Engine (Normal Flow 3 & 5) ======
// Displays read-only logs for review
function renderLogs(logsArray) {
    logsTableBody.innerHTML = '';
    systemMsgBox.classList.add('hidden');

    // Alternative Flow 2: If no operation logs are available
    if (logsArray.length === 0) {
        logsTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="px-6 py-20 text-center">
                    <div class="flex flex-col items-center justify-center">
                        <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center text-slate-300 mb-4">
                           <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        </div>
                        <p class="text-slate-600 text-base font-bold">No logs found matching your criteria</p>
                        <p class="text-slate-400 text-sm mt-1 mb-2">Try adjusting the filters or searching for another user.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    logsArray.forEach(log => {
        // Find the user details from usersData based on target_user_id
        const targetUser = usersData.find(u => u.user_id === log.target_user_id);
        const userName = targetUser ? targetUser.username : `Unknown (ID: ${log.target_user_id})`;
        const userEmail = targetUser ? targetUser.email : 'N/A';

        // Styling based on Action severity
        let actionStyle = 'bg-slate-100 text-slate-700'; 
        if (log.action_type.includes('Suspended') || log.action_type.includes('Failed')) {
            actionStyle = 'bg-rose-100 text-rose-700 border border-rose-200';
        } else if (log.action_type.includes('Reactivated')) {
            actionStyle = 'bg-emerald-100 text-emerald-700 border border-emerald-200';
        } else if (log.action_type.includes('Updated')) {
            actionStyle = 'bg-blue-100 text-blue-700 border border-blue-200';
        }

        const row = `
            <tr class="hover:bg-slate-50 transition duration-150">
                <td class="px-6 py-4 align-top">
                    <p class="font-bold text-slate-800">${log.created_at.split(' ')[0]}</p>
                    <p class="text-xs text-slate-500 mt-1">${log.created_at.split(' ')[1]}</p>
                    <p class="text-[11px] font-mono bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded mt-2 inline-block">IP: ${log.ip_address}</p>
                </td>
                <td class="px-6 py-4 align-top">
                    <p class="font-bold text-slate-900">${userName}</p>
                    <p class="text-xs text-slate-500 leading-relaxed mt-0.5">${userEmail}</p>
                </td>
                <td class="px-6 py-4 align-top">
                    <span class="inline-flex px-2.5 py-1 rounded-md text-xs font-bold shadow-sm ${actionStyle}">
                        ${log.action_type}
                    </span>
                </td>
                <td class="px-6 py-4 align-top">
                    <p class="text-sm text-slate-600 leading-relaxed bg-slate-50 p-2 rounded-lg border border-slate-100">${log.details}</p>
                </td>
            </tr>
        `;
        logsTableBody.innerHTML += row;
    });
}

// ====== Search & Filter Logic (Normal Flow 4 & Sub Flow 1) ======
function handleLogSearch() {
    const searchVal = logSearchInput.value.toLowerCase().trim();
    const actionVal = actionFilter.value;
    const dateVal = dateFilter.value; // e.g. "2023-10-24"

    systemMsgBox.classList.add('hidden');

    // 1. Identify Target Users based on search string
    let matchedUserIds = [];
    if (searchVal) {
        const matchedUsers = usersData.filter(u => u.username.toLowerCase().includes(searchVal) || u.email.toLowerCase().includes(searchVal));
        
        // Alternative Flow 1: Target user account cannot be found
        if (matchedUsers.length === 0) {
            systemMsgBox.innerHTML = `<strong>Search Error:</strong> No target user account found matching "${searchVal}".`;
            systemMsgBox.className = "mb-6 p-4 rounded-xl text-sm border bg-amber-50 text-amber-700 border-amber-200 font-medium";
            systemMsgBox.classList.remove('hidden');
            renderLogs([]); // Empty logs
            return;
        }
        
        matchedUserIds = matchedUsers.map(u => u.user_id);
    }

    // 2. Filter the Logs Array
    const filteredLogs = logsData.filter(log => {
        // Filter by specific user IDs if search exists
        const matchesUser = searchVal === '' || matchedUserIds.includes(log.target_user_id);
        
        // Filter by Action Type partial match
        const matchesAction = actionVal === 'all' || log.action_type.includes(actionVal);
        
        // Filter by Date match
        const matchesDate = dateVal === '' || log.created_at.startsWith(dateVal);

        return matchesUser && matchesAction && matchesDate;
    });

    renderLogs(filteredLogs);
}

// ====== Events ======
searchLogsBtn.addEventListener('click', handleLogSearch);

clearLogsBtn.addEventListener('click', () => {
    logSearchInput.value = '';
    actionFilter.value = 'all';
    dateFilter.value = '';
    systemMsgBox.classList.add('hidden');
    renderLogs(logsData); // Show all default logs
});

// Init load
renderLogs(logsData);