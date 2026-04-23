import { checkAuth, logout } from "./js/auth.js";

document.addEventListener("DOMContentLoaded", () => {
    const user = checkAuth(false);
    if (user) {
        // Update user profile in sidebar
        const nameEl = document.getElementById("user-display-name");
        const roleEl = document.getElementById("user-role-display");
        const initialEl = document.getElementById("user-initial");
        
        if (nameEl) nameEl.innerText = user.username;
        if (roleEl) roleEl.innerText = user.role;
        if (initialEl) initialEl.innerText = user.username.charAt(0).toUpperCase();

        // Inject Admin Link
        if (user.role === "Admin") {
            const adminNav = document.getElementById("admin-nav-item");
            if (adminNav) {
                adminNav.innerHTML = \`
                    <a href="admin.html" class="flex items-center gap-3 px-4 py-3 text-indigo-400 hover:bg-indigo-900/20 rounded-xl font-semibold transition-all">
                        <i class="fas fa-user-shield"></i> Admin Console
                    </a>
                \`;
            }
        }

        const logoutBtn = document.getElementById("nav-logout");
        if (logoutBtn) {
            logoutBtn.onclick = (e) => {
                e.preventDefault();
                logout();
            };
        }
    }
});
