// UC 57 DOM Elements
const tableBody = document.getElementById('tableBody');
const searchInput = document.getElementById('searchInput');
const roleFilter = document.getElementById('roleFilter');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');

// UC 57: Render Data
function renderTable(dataArray) {
    tableBody.innerHTML = '';

    // Alternative Flow 1: No results found
    if (dataArray.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="px-6 py-16 text-center">
                    <div class="flex flex-col items-center justify-center">
                        <svg class="w-12 h-12 text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        <p class="text-slate-500 text-sm font-medium">No users found matching your criteria</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    dataArray.forEach(user => {
        // Status Badges
        let statusBadge = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700"><span class="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5"></span>Pending</span>`;
        if (user.status === 'Active') {
            statusBadge = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>Active</span>`;
        } else if (user.status === 'Suspended') {
            statusBadge = `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-rose-100 text-rose-700"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5"></span>Suspended</span>`;
        }

        // Role Badge
        let roleBadge = `<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">${user.role_name}</span>`;

        // ★ 这里是极其重要的一步：链接到 58，并且在 URL 后面附带 userId
        let actionButtons = `
        <a href="uc58.html?userId=${user.user_id}" class="text-blue-600 font-semibold text-sm hover:bg-blue-50 px-3 py-1.5 rounded transition">Edit</a>
        <a href="uc61.html?userId=${user.user_id}" class="${user.status === 'Suspended' ? 'text-emerald-600 hover:bg-emerald-50' : 'text-rose-600 hover:bg-rose-50'} font-semibold text-sm px-3 py-1.5 rounded transition">
                ${user.status === 'Suspended' ? 'Reactivate' : 'Suspend'}
        `;
        const row = `
            <tr class="hover:bg-slate-50 transition duration-150 ease-in-out">
                <td class="px-6 py-4">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 font-bold border border-blue-200">
                            ${user.username.charAt(0).toUpperCase()}
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-semibold text-slate-900">${user.username}</div>
                            <div class="text-sm text-slate-500">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">${roleBadge}</td>
                <td class="px-6 py-4 whitespace-nowrap">${statusBadge}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                    ${actionButtons}
                </td>
            </tr>
        `;
        tableBody.innerHTML += row;
    });
}

// UC 57: Filter Logic
function handleSearch() {
    const searchVal = searchInput.value.toLowerCase().trim();
    const roleVal = roleFilter.value;

    const filteredData = usersData.filter(user => {
        const matchText = user.username.toLowerCase().includes(searchVal) || user.email.toLowerCase().includes(searchVal);
        const matchRole = (roleVal === 'all') || (user.role_name === roleVal);
        return matchText && matchRole;
    });

    renderTable(filteredData);
}

// Event Listeners
searchBtn.addEventListener('click', handleSearch);

clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    roleFilter.value = 'all';
    renderTable(usersData);
});

// Initialize
renderTable(usersData);