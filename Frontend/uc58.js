// 1. 获取 DOM 元素
const editUsername = document.getElementById('editUsername');
const editEmail = document.getElementById('editEmail');
const editRole = document.getElementById('editRole');
const saveBtn = document.getElementById('saveBtn');
const cancelBtn = document.getElementById('cancelBtn');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');

// 2. 从 URL 中获取传过来的用户 ID (比如从 57 的页面带着 ?userId=1 过来)
const urlParams = new URLSearchParams(window.location.search);
const targetUserId = parseInt(urlParams.get('userId'));

// 3. Normal Flow 2: 页面加载时，利用这个 ID 自动去把他的旧信息找出来填上
let currentUser = null;

if (targetUserId) {
    currentUser = usersData.find(u => u.user_id === targetUserId);
    
    if (currentUser) {
        editUsername.value = currentUser.username;
        editEmail.value = currentUser.email;
        editRole.value = currentUser.role_name;
    } else {
        errorMessage.textContent = "Error: User not found in database.";
        errorMessage.classList.remove('hidden');
    }
} else {
    // 如果没有带 ID 跳转过来（比如你直接双击这个html），就显示报错
    errorMessage.textContent = "No user selected. Please go back to the Search page.";
    errorMessage.classList.remove('hidden');
    saveBtn.disabled = true; // 禁用保存按钮
}

// 4. Normal Flow 4 & 5: 点击保存验证并更新
saveBtn.addEventListener('click', () => {
    const newName = editUsername.value.trim();
    const newEmail = editEmail.value.trim();
    
    errorMessage.classList.add('hidden');

    // Alternative Flow 1: 空值验证
    if (!newName || !newEmail) {
        errorMessage.textContent = "Error: Username and Email are required fields.";
        errorMessage.classList.remove('hidden');
        return;
    }

    // Alternative Flow 2: 邮箱被盗用验证
    const emailTaken = usersData.some(u => u.email.toLowerCase() === newEmail.toLowerCase() && u.user_id !== targetUserId);
    if (emailTaken) {
        errorMessage.textContent = "Error: This email address is already in use by another account.";
        errorMessage.classList.remove('hidden');
        return;
    }

    // 更新 data.js （在真实环境里这里会是个发给后端的保存接口）
    if (currentUser) {
        currentUser.username = newName;
        currentUser.email = newEmail;
        currentUser.role_name = editRole.value;
    }

    // Normal Flow 6: 显示翠绿色成功块，两秒后跳走
    successMessage.classList.remove('hidden');
    
    // 给老师或者观众看的两秒延迟（假装系统在存储）
    setTimeout(() => {
        window.location.href = 'index.html'; // 返回完美的 57 表格
    }, 2000);
});

// 5. Sub-Flow 1: 用户点击 Cancel，啥也不干，原路退回 57 表格
cancelBtn.addEventListener('click', () => {
    window.location.href = 'index.html'; 
});