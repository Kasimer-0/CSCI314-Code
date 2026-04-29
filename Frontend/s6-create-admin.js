// US #2 + #3 — User Admin creates a new admin account & profile (with role + permissions).
// Picking a role pre-checks its default permission set; the admin can then tweak permissions
// individually before sending the invite. Submit appends a Pending user to usersData and
// redirects to the user-management screen with a confirmation toast.

const form = document.getElementById('createAdminForm');
const firstNameInput = document.getElementById('firstName');
const lastNameInput = document.getElementById('lastName');
const workEmailInput = document.getElementById('workEmail');
const employeeIdInput = document.getElementById('employeeId');
const departmentInput = document.getElementById('department');
const phoneInput = document.getElementById('phone');
const submitBtn = document.getElementById('submitBtn');
const formError = document.getElementById('formError');

let selectedRole = 'User Admin';

// ---------- role card selection ----------
function paintRoleSelection() {
    document.querySelectorAll('.role-card').forEach(card => {
        const isSelected = card.dataset.role === selectedRole;
        card.className = `role-card bg-slate-800 ${isSelected ? 'border-blue-500' : 'border-slate-700'} border-2 rounded-xl p-4 cursor-pointer block`;
        const radio = card.querySelector('.role-radio');
        if (isSelected) {
            radio.className = 'role-radio w-4 h-4 rounded-full border-2 border-blue-500 flex items-center justify-center';
            radio.innerHTML = '<span class="w-2 h-2 rounded-full bg-blue-500"></span>';
        } else {
            radio.className = 'role-radio w-4 h-4 rounded-full border-2 border-slate-600';
            radio.innerHTML = '';
        }
    });
}

function applyDefaultPermissions(role) {
    const defaults = (window.FS.ADMIN_ROLE_DEFAULTS[role] || {}).defaultPermissions || [];
    document.querySelectorAll('.perm-check').forEach(cb => {
        cb.checked = defaults.includes(cb.dataset.perm);
    });
}

document.getElementById('roleGrid').addEventListener('click', (e) => {
    const card = e.target.closest('.role-card');
    if (!card) return;
    selectedRole = card.dataset.role;
    paintRoleSelection();
    applyDefaultPermissions(selectedRole);
});

paintRoleSelection();
applyDefaultPermissions(selectedRole);

// ---------- submit ----------
function showError(msg) {
    formError.textContent = msg;
    formError.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    formError.classList.add('hidden');

    const firstName = firstNameInput.value.trim();
    const lastName = lastNameInput.value.trim();
    const workEmail = workEmailInput.value.trim();
    const employeeId = employeeIdInput.value.trim();
    const department = departmentInput.value;
    const phone = phoneInput.value.trim();

    if (!firstName || !lastName || !workEmail || !employeeId) {
        showError('First name, last name, work email and employee ID are required.');
        return;
    }
    if (!workEmail.includes('@')) {
        showError('Enter a valid work email.');
        return;
    }
    if (usersData.some(u => u.email.toLowerCase() === workEmail.toLowerCase())) {
        showError('Another account already uses that work email.');
        return;
    }

    const permissions = Array.from(document.querySelectorAll('.perm-check'))
        .filter(cb => cb.checked)
        .map(cb => cb.dataset.perm);

    const newId = usersData.reduce((max, u) => Math.max(max, u.user_id), 0) + 1;
    const today = new Date().toISOString().slice(0, 10);

    usersData.push({
        user_id: newId,
        username: `${firstName} ${lastName}`,
        first_name: firstName,
        last_name: lastName,
        email: workEmail,
        role_name: selectedRole,
        status: 'Pending',  // becomes Active once they accept the invite + set a password
        phone,
        location: '',
        date_of_birth: '',
        bio: '',
        member_since: today,
        last_signin: '—',
        last_active_at: null,
        two_factor: false,
        email_verified: false,
        employee_id: employeeId,
        department,
        work_email: workEmail,
        permissions
    });

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>✓</span> Invite sent';
    setTimeout(() => {
        window.location.href = 'index-UC57.html';
    }, 600);
});
