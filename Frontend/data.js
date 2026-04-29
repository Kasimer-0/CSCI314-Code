// ====== data.js ======
// Mock data for the Fundraising System IAM module.
//
// `usersData` schema (all fields optional except user_id, username, email, role_name, status — those are
// relied on by the legacy UC57-62 pages):
//   user_id        : number
//   username       : string  (display name; for individuals == "First Last")
//   first_name     : string
//   last_name      : string
//   email          : string
//   role_name      : 'Fundraiser' | 'Donee' | 'User Admin' | 'Platform Admin' | 'Super Admin' | 'Platform Manager'
//   status         : 'Active' | 'Pending' | 'Suspended' | 'Rejected'
//   phone          : string
//   location       : string
//   date_of_birth  : 'YYYY-MM-DD'
//   bio            : string
//   member_since   : 'YYYY-MM-DD'
//   last_signin    : 'YYYY-MM-DD HH:MM' + device note (display only)
//   last_active_at : ISO string used to render "2 min ago" / "Today" / "5 days ago"
//   two_factor     : boolean
//   email_verified : boolean
//   stats          : { donations, saved, active }   // Donee-side stats shown on view profile
//   employee_id    : string                          // admin-only
//   department     : string                          // admin-only
//   work_email     : string                          // admin-only
//   permissions    : string[]                        // admin-only (granular permissions)
//
// Permission tokens used by the Create Admin flow + role badges:
//   approve_fundraiser_registrations
//   suspend_reactivate_user_accounts
//   view_audit_logs
//   export_user_data_csv
//
// Admin role defaults (used as a hint by the Create Admin form):
const ADMIN_ROLE_DEFAULTS = {
    'User Admin': {
        description: 'Manage user accounts, roles, and registration approvals.',
        defaultPermissions: ['approve_fundraiser_registrations', 'suspend_reactivate_user_accounts']
    },
    'Platform Admin': {
        description: 'Configure categories, content moderation, and reports.',
        defaultPermissions: ['view_audit_logs']
    },
    'Super Admin': {
        description: 'Full system access including audit logs and billing controls.',
        defaultPermissions: [
            'approve_fundraiser_registrations',
            'suspend_reactivate_user_accounts',
            'view_audit_logs',
            'export_user_data_csv'
        ]
    }
};

const PERMISSION_LABELS = {
    approve_fundraiser_registrations: 'Approve fundraiser registrations',
    suspend_reactivate_user_accounts: 'Suspend or reactivate user accounts',
    view_audit_logs: 'View audit logs',
    export_user_data_csv: 'Export user data (CSV)'
};

const usersData = [
    // Existing UC57-62 users (extended with profile fields)
    {
        user_id: 1,
        username: 'Alex Johnson',
        first_name: 'Alex', last_name: 'Johnson',
        email: 'alex.johnson@example.com',
        role_name: 'Fundraiser', status: 'Active',
        phone: '+1 (415) 555-0182',
        location: 'San Francisco, CA',
        date_of_birth: '1991-07-22',
        bio: 'Community organizer focused on youth education and clean water initiatives across West Africa.',
        member_since: '2024-04-12',
        last_signin: '2026-04-28 09:14 · Chrome on macOS',
        last_active_at: '2026-04-28T09:14:00',
        two_factor: false,
        email_verified: true,
        stats: { donations: 24, saved: 8, active: 3 }
    },
    {
        user_id: 2,
        username: 'Green Earth Foundation',
        first_name: 'Green Earth', last_name: 'Foundation',
        email: 'contact@greenearth.org',
        role_name: 'Donee', status: 'Suspended',
        phone: '+1 (212) 555-0144',
        location: 'New York, NY',
        date_of_birth: '2010-03-01',
        bio: 'Reforestation and watershed protection across the Northeast.',
        member_since: '2023-01-04',
        last_signin: '2026-04-25 18:02 · Safari on iOS',
        last_active_at: '2026-04-25T18:02:00',
        two_factor: true,
        email_verified: true,
        stats: { donations: 0, saved: 0, active: 0 }
    },
    {
        user_id: 3,
        username: 'Victoria Admin',
        first_name: 'Victoria', last_name: 'Adekunle',
        email: 'vadmin@example.com',
        role_name: 'User Admin', status: 'Active',
        phone: '+1 (646) 555-0274',
        location: 'New York, NY',
        date_of_birth: '1988-09-30',
        bio: 'Heads the Trust & Safety team. Reviews registration requests and handles escalations.',
        member_since: '2022-08-15',
        last_signin: '2026-04-28 08:01 · Chrome on Windows',
        last_active_at: '2026-04-28T08:01:00',
        two_factor: true,
        email_verified: true,
        employee_id: 'GH-04982',
        department: 'Trust & Safety',
        work_email: 'vadmin@givehub.org',
        permissions: [
            'approve_fundraiser_registrations',
            'suspend_reactivate_user_accounts',
            'view_audit_logs'
        ]
    },
    {
        user_id: 4,
        username: 'Tom Smith',
        first_name: 'Tom', last_name: 'Smith',
        email: 'tom.smith@example.com',
        role_name: 'Fundraiser', status: 'Pending',
        phone: '+1 (303) 555-0119',
        location: 'Denver, CO',
        date_of_birth: '1995-11-14',
        bio: '',
        member_since: '2026-04-20',
        last_signin: '—',
        last_active_at: null,
        two_factor: false,
        email_verified: false,
        stats: { donations: 0, saved: 0, active: 0 }
    },
    {
        user_id: 5,
        username: 'Ocean Rescue Team',
        first_name: 'Ocean', last_name: 'Rescue',
        email: 'hello@oceanrescue.org',
        role_name: 'Donee', status: 'Active',
        phone: '+1 (808) 555-0166',
        location: 'Honolulu, HI',
        date_of_birth: '2015-06-08',
        bio: 'Marine wildlife rehabilitation and beach restoration across the Pacific.',
        member_since: '2023-11-21',
        last_signin: '2026-04-27 22:40 · Firefox on Linux',
        last_active_at: '2026-04-27T22:40:00',
        two_factor: false,
        email_verified: true,
        stats: { donations: 12, saved: 4, active: 2 }
    },

    // Extra users to populate screen 7 + demonstrate admin sub-roles
    {
        user_id: 6,
        username: 'Aisha Mensah',
        first_name: 'Aisha', last_name: 'Mensah',
        email: 'aisha.mensah@gmail.com',
        role_name: 'Donee', status: 'Active',
        phone: '+1 (415) 555-0182',
        location: 'San Francisco, CA',
        date_of_birth: '1993-03-14',
        bio: 'Community organizer focused on youth education and clean water initiatives across West Africa.',
        member_since: '2024-04-12',
        last_signin: '2026-04-28 09:14 · Chrome on macOS',
        last_active_at: '2026-04-28T09:12:00', // ~2 min ago vs currentDate
        two_factor: false,
        email_verified: true,
        stats: { donations: 24, saved: 8, active: 3 }
    },
    {
        user_id: 7,
        username: 'Marcus Steele',
        first_name: 'Marcus', last_name: 'Steele',
        email: 'marcus@steeleinitiative.org',
        role_name: 'Fundraiser', status: 'Active',
        phone: '+1 (312) 555-0301',
        location: 'Chicago, IL',
        date_of_birth: '1986-01-09',
        bio: 'Runs the Steele Initiative, focused on inner-city after-school programs.',
        member_since: '2024-03-28',
        last_signin: '2026-04-28 08:14 · Chrome on Windows',
        last_active_at: '2026-04-28T08:14:00', // ~1 hr ago
        two_factor: true,
        email_verified: true,
        stats: { donations: 0, saved: 0, active: 0 }
    },
    {
        user_id: 8,
        username: 'Linh Nguyen',
        first_name: 'Linh', last_name: 'Nguyen',
        email: 'linh.nguyen@givehub.org',
        role_name: 'User Admin', status: 'Active',
        phone: '+1 (646) 555-0274',
        location: 'Brooklyn, NY',
        date_of_birth: '1990-12-02',
        bio: 'User Admin focused on registration approvals and account hygiene.',
        member_since: '2024-01-08',
        last_signin: '2026-04-28 06:04 · Chrome on macOS',
        last_active_at: '2026-04-28T06:04:00', // Today
        two_factor: true,
        email_verified: true,
        employee_id: 'GH-06121',
        department: 'Trust & Safety',
        work_email: 'linh.nguyen@givehub.org',
        permissions: [
            'approve_fundraiser_registrations',
            'suspend_reactivate_user_accounts'
        ]
    },
    {
        user_id: 9,
        username: 'Kofi Asante',
        first_name: 'Kofi', last_name: 'Asante',
        email: 'kofi.a@gmail.com',
        role_name: 'Donee', status: 'Pending',
        phone: '',
        location: 'Accra, GH',
        date_of_birth: '1998-05-19',
        bio: '',
        member_since: '2025-06-02',
        last_signin: '—',
        last_active_at: null,
        two_factor: false,
        email_verified: false,
        stats: { donations: 0, saved: 0, active: 0 }
    },
    {
        user_id: 10,
        username: 'Sara Whitfield',
        first_name: 'Sara', last_name: 'Whitfield',
        email: 'sara.w@brightfutures.org',
        role_name: 'Fundraiser', status: 'Suspended',
        phone: '+44 20 7946 0233',
        location: 'London, UK',
        date_of_birth: '1989-08-25',
        bio: 'Bright Futures lead — currently under review.',
        member_since: '2024-02-15',
        last_signin: '2026-04-25 12:00 · Chrome on Windows',
        last_active_at: '2026-04-25T12:00:00', // 3 days ago
        two_factor: false,
        email_verified: true,
        stats: { donations: 0, saved: 0, active: 0 }
    },
    {
        user_id: 11,
        username: 'Daniel Park',
        first_name: 'Daniel', last_name: 'Park',
        email: 'd.park@givehub.org',
        role_name: 'Platform Manager', status: 'Active',
        phone: '+1 (206) 555-0119',
        location: 'Seattle, WA',
        date_of_birth: '1984-04-06',
        bio: 'Owns the Platform service catalog and category lifecycle.',
        member_since: '2023-09-12',
        last_signin: '2026-04-28 04:30 · Chrome on macOS',
        last_active_at: '2026-04-28T04:30:00', // 5 hr ago
        two_factor: true,
        email_verified: true,
        employee_id: 'GH-03110',
        department: 'Platform Operations',
        work_email: 'd.park@givehub.org',
        permissions: ['view_audit_logs']
    },
    {
        user_id: 12,
        username: 'Priya Iyer',
        first_name: 'Priya', last_name: 'Iyer',
        email: 'priya.iyer@gmail.com',
        role_name: 'Donee', status: 'Active',
        phone: '+91 98765 43210',
        location: 'Bengaluru, IN',
        date_of_birth: '1994-02-11',
        bio: 'Maker-space mentor in Bengaluru — looking for STEM kit donations.',
        member_since: '2025-03-30',
        last_signin: '2026-04-28 09:02 · Safari on iOS',
        last_active_at: '2026-04-28T09:02:00', // 12 min ago
        two_factor: false,
        email_verified: true,
        stats: { donations: 4, saved: 2, active: 1 }
    },
    {
        user_id: 13,
        username: 'Tomás Reyes',
        first_name: 'Tomás', last_name: 'Reyes',
        email: 'tomas.r@hopebridge.org',
        role_name: 'Fundraiser', status: 'Active',
        phone: '+1 (786) 555-0142',
        location: 'Miami, FL',
        date_of_birth: '1987-10-30',
        bio: 'Hopebridge logistics — disaster-response supply runs.',
        member_since: '2024-05-11',
        last_signin: '2026-04-27 19:55 · Chrome on Android',
        last_active_at: '2026-04-27T19:55:00', // Yesterday
        two_factor: true,
        email_verified: true,
        stats: { donations: 0, saved: 0, active: 0 }
    },
    {
        user_id: 14,
        username: 'Jordan Chen',
        first_name: 'Jordan', last_name: 'Chen',
        email: 'jordan.chen@givehub.org',
        role_name: 'Super Admin', status: 'Active',
        phone: '+1 (415) 555-0900',
        location: 'San Francisco, CA',
        date_of_birth: '1982-06-17',
        bio: 'Super Admin — owns billing, audit, and account lifecycle controls.',
        member_since: '2022-05-01',
        last_signin: '2026-04-28 07:30 · Chrome on macOS',
        last_active_at: '2026-04-28T07:30:00',
        two_factor: true,
        email_verified: true,
        employee_id: 'GH-00001',
        department: 'Executive',
        work_email: 'jordan.chen@givehub.org',
        permissions: [
            'approve_fundraiser_registrations',
            'suspend_reactivate_user_accounts',
            'view_audit_logs',
            'export_user_data_csv'
        ]
    },
    {
        user_id: 15,
        username: 'Maya Okafor',
        first_name: 'Maya', last_name: 'Okafor',
        email: 'maya.okafor@givehub.org',
        role_name: 'Platform Admin', status: 'Pending',
        phone: '+1 (646) 555-0274',
        location: 'New York, NY',
        date_of_birth: '1992-09-09',
        bio: 'Joining Trust & Safety as a Platform Admin — invite pending.',
        member_since: '2026-04-27',
        last_signin: '—',
        last_active_at: null,
        two_factor: false,
        email_verified: false,
        employee_id: 'GH-04982',
        department: 'Trust & Safety',
        work_email: 'maya.okafor@givehub.org',
        permissions: ['view_audit_logs']
    }
];

// ====== Audit logs (kept compatible with UC62) ======
// Field names match the schema defined in the S1-12.pdf database dump:
// log_id, admin_id, target_user_id, action_type, ip_address, created_at
// ('details' is added for frontend display purposes)
const logsData = [
    { log_id: 101, admin_id: 3, target_user_id: 2, action_type: 'Account Suspended', ip_address: '192.168.1.45', created_at: '2023-10-24 14:30:00', details: 'Violation of rule #4: Spamming.' },
    { log_id: 102, admin_id: 3, target_user_id: 2, action_type: 'Profile Updated', ip_address: '192.168.1.45', created_at: '2023-10-24 10:15:00', details: 'Admin corrected organization email.' },
    { log_id: 103, admin_id: null, target_user_id: 2, action_type: 'Failed Login', ip_address: '45.22.11.90', created_at: '2023-10-23 23:45:00', details: 'Invalid password entered 5 times.' },
    { log_id: 104, admin_id: 3, target_user_id: 1, action_type: 'Account Reactivated', ip_address: '192.168.1.45', created_at: '2023-10-20 09:00:00', details: 'User appealed successfully.' },
    { log_id: 105, admin_id: null, target_user_id: 1, action_type: 'Fundraising Post Created', ip_address: '77.88.99.11', created_at: '2023-10-18 16:20:00', details: 'Created post ID #889.' }
];

// ====== Tiny helpers shared across the new screens ======
// Keep these on `window` so legacy UC57-62 scripts stay untouched, while the new s1-s7 scripts
// have a single source of truth.
window.FS = window.FS || {};
window.FS.ADMIN_ROLE_DEFAULTS = ADMIN_ROLE_DEFAULTS;
window.FS.PERMISSION_LABELS = PERMISSION_LABELS;

window.FS.isAdminRole = function (role) {
    return role === 'User Admin' || role === 'Platform Admin' || role === 'Super Admin';
};

window.FS.formatDate = function (isoOrYmd) {
    if (!isoOrYmd) return '—';
    const d = new Date(isoOrYmd);
    if (isNaN(d.getTime())) return isoOrYmd;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

window.FS.formatDateLong = function (isoOrYmd) {
    if (!isoOrYmd) return '—';
    const d = new Date(isoOrYmd);
    if (isNaN(d.getTime())) return isoOrYmd;
    return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
};

// "Today's date" is fixed in the demo so relative timestamps look right against the seeded data.
window.FS.NOW = new Date('2026-04-28T09:14:00');

window.FS.relativeTime = function (iso) {
    if (!iso) return '—';
    const t = new Date(iso).getTime();
    if (isNaN(t)) return '—';
    const diffMs = window.FS.NOW.getTime() - t;
    const min = Math.floor(diffMs / 60000);
    if (min < 1) return 'Just now';
    if (min < 60) return `${min} min ago`;
    const hr = Math.floor(min / 60);
    if (hr < 24) return `${hr} hr ago`;
    const days = Math.floor(hr / 24);
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return window.FS.formatDate(iso);
};

window.FS.initials = function (name) {
    if (!name) return '?';
    const parts = String(name).trim().split(/\s+/).slice(0, 2);
    return parts.map(p => p.charAt(0).toUpperCase()).join('');
};
