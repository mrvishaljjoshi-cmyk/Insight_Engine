import glob

js_code = """
        window.updateProfile = async () => {
            const btn = document.getElementById('btn-update');
            if(!btn) return;
            const orig = btn.innerText;
            btn.innerText = 'Sending...';
            btn.disabled = true;
            try {
                const payload = {};
                const u = document.getElementById('profile-user'); if(u && u.value) payload.username = u.value;
                const e = document.getElementById('profile-email'); if(e && e.value) payload.email = e.value;
                const m = document.getElementById('profile-mobile'); if(m && m.value) payload.mobile_no = m.value;
                const t = document.getElementById('profile-telegram'); if(t && t.value) payload.telegram_id = t.value;
                
                // fallback if getAuthHeaders is not globally available, we know it's in the module
                // but we can just use localStorage token directly
                const token = localStorage.getItem('token');
                const headers = { 'Content-Type': 'application/json' };
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const res = await fetch('/api/auth/me', {
                    method: 'PATCH',
                    headers: headers,
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) alert(data.message || 'Update request sent!');
                else alert('Error: ' + data.detail);
                if(window.toggleProfile) window.toggleProfile();
            } catch (e) {
                alert('Error updating profile: ' + e.message);
            } finally {
                btn.innerText = orig;
                btn.disabled = false;
            }
        };
"""

files = ['ai_summary.html', 'trading.html', 'options.html', 'admin.html', 'dashboard.html']
for filename in files:
    f = 'ACTIVE/Insight_Engine/frontend_native/' + filename
    with open(f, 'r') as file:
        content = file.read()
    
    if 'window.updateProfile = async () => {' not in content:
        # replace the last </script> with the new code
        content = content.replace('window.updateProfile = () => alert("Profile update feature coming soon");', '')
        content = content.replace('window.updateProfile = () => alert("Profile update coming soon");', '')
        content = content.replace('</script>\n</body>', js_code + '\n    </script>\n</body>')
        
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated {f}")

