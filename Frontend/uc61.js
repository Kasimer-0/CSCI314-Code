// 1. DOM 元素抓取
const targetName = document.getElementById('targetName');
const targetEmail = document.getElementById('targetEmail');
const currentStatusBadge = document.getElementById('currentStatusBadge');
const actionWarning = document.getElementById('actionWarning');
const reasonInput = document.getElementById('reasonInput');
const confirmBtn = document.getElementById('confirmBtn');
const cancelBtn = document.getElementById('cancelBtn');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');

// 2. 解析网址里的用户 ID
const urlParams = new URLSearchParams(window.location.search);
const targetUserId = parseInt(urlParams.get('userId'));

let currentUser = null;
let targetActionStatus = ''; // 记录即将变为什么状态 (Active or Suspended)

// 3. 页面初始化加载 (Normal Flow 2)
if (targetUserId) {
    currentUser = usersData.find(u => u.user_id === targetUserId);
    
    // Alternative Flow 1: 找不到目标账户
    if (!currentUser) {
        showError("Error: The target user account cannot be found.");
        disableForm();
    } else {
        // 成功找到用户，渲染基本信息
        targetName.textContent = currentUser.username;
        targetEmail.textContent = currentUser.email;
        
        setupDynamicUI(currentUser.status);
    }
} else {
    // 没带 ID 直接打开这页的异常处理
    showError("No target user selected. Please return to the User Management page.");
    disableForm();
}

// 4. 根据用户当前状态，智能切换 UI 颜色和文案 (Normal Flow 3)
function setupDynamicUI(status) {
    if (status === 'Active') {
        // 准备进行封禁操作 (Suspend)
        targetActionStatus = 'Suspended';
        
        currentStatusBadge.innerHTML = `<span class="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold border border-emerald-200">Current: Active</span>`;
        
        actionWarning.className = "p-4 rounded-xl text-sm font-medium border bg-rose-50 text-rose-700 border-rose-200";
        actionWarning.innerHTML = `<strong>Warning:</strong> You are about to SUSPEND this active account. They will be restricted from platform functions.`;
        
        confirmBtn.textContent = "Suspend Account";
        confirmBtn.classList.add("bg-rose-600", "hover:bg-rose-700");

    } else if (status === 'Suspended') {
        // 准备进行解封操作 (Reactivate)
        targetActionStatus = 'Active';
        
        currentStatusBadge.innerHTML = `<span class="bg-rose-100 text-rose-700 px-3 py-1 rounded-full text-xs font-bold border border-rose-200">Current: Suspended</span>`;
        
        actionWarning.className = "p-4 rounded-xl text-sm font-medium border bg-emerald-50 text-emerald-700 border-emerald-200";
        actionWarning.innerHTML = `<strong>Notice:</strong> You are about to REACTIVATE this suspended account. They will regain platform access.`;
        
        confirmBtn.textContent = "Reactivate Account";
        confirmBtn.classList.add("bg-emerald-600", "hover:bg-emerald-700");
    } else {
        // 如果是 Pending 等其他状态
        showError(`Error: Users with status '${status}' cannot be managed here.`);
        disableForm();
    }
}

// 5. 确认操作 (Normal Flow 5)
confirmBtn.addEventListener('click', () => {
    errorMessage.classList.add('hidden');
    const reasonText = reasonInput.value.trim();

    // Alternative Flow 2: 没写原因，立刻暴红阻拦！
    if (!reasonText) {
        showError("Action Denied: You must provide a reason for the status change.");
        // 让文本框红一下引起注意
        reasonInput.classList.add("border-rose-500", "ring-1", "ring-rose-500");
        setTimeout(() => reasonInput.classList.remove("border-rose-500", "ring-1", "ring-rose-500"), 2000);
        return;
    }

    // Normal Flow 6: 更新状态并显示成功信息
    if (currentUser) {
        currentUser.status = targetActionStatus;
        // （真实开发中，这里还会把 reasonText 存进 Audit Logs 里）
        
        successMessage.textContent = `Success: Account gracefully marked as ${targetActionStatus}. Returning to User Management...`;
        successMessage.classList.remove('hidden');
        confirmBtn.disabled = true;
        
        // 2 秒后回到 57 搜索页
        setTimeout(() => {
            window.location.href = 'index.html'; 
        }, 2000);
    }
});

// 6. 取消操作 (Sub-Flow 1 & 2)
cancelBtn.addEventListener('click', () => {
    window.location.href = 'index.html'; 
});

function showError(msg) {
    errorMessage.innerHTML = msg;
    errorMessage.classList.remove('hidden');
}

function disableForm() {
    reasonInput.disabled = true;
    confirmBtn.disabled = true;
    confirmBtn.classList.add("opacity-50", "cursor-not-allowed");
}