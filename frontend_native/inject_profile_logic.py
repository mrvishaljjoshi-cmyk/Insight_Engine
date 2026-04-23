import glob

js_code = """
        // Profile Modal Logic
        window.toggleProfileEdit = (show) => {
            document.getElementById('profile-view-section').classList.toggle('hidden', show);
            document.getElementById('profile-edit-section').classList.toggle('hidden', !show);
        };

        window.togglePasswordSection = (show) => {
            document.getElementById('profile-view-section').classList.toggle('hidden', show);
            document.getElementById('profile-password-section').classList.toggle('hidden', !show);
        };

        window.updateProfile = async () => {
            const btn = document.getElementById('btn-update-profile');
            const orig = btn.innerText; btn.innerText = 'Requesting...'; btn.disabled = true;
            try {
                const payload = {
                    username: document.getElementById('profile-user').value,
                    email: document.getElementById('profile-email').value,
                    mobile_no: document.getElementById('profile-mobile').value,
                    telegram_id: document.getElementById('profile-telegram').value
                };
                const token = localStorage.getItem('token');
                const res = await fetch('/api/auth/me', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                alert(data.message || 'Update request sent to Admin!');
                window.toggleProfile();
            } catch (e) { alert('Error: ' + e.message); }
            finally { btn.innerText = orig; btn.disabled = false; }
        };

        window.changePassword = async () => {
            const btn = document.getElementById('btn-change-pass');
            const orig = btn.innerText; btn.innerText = 'Updating...'; btn.disabled = true;
            try {
                const payload = {
                    current_password: document.getElementById('pass-current').value,
                    new_password: document.getElementById('pass-new').value
                };
                const token = localStorage.getItem('token');
                const res = await fetch('/api/auth/change-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) { alert('Password changed successfully!'); window.toggleProfile(); }
                else { alert('Error: ' + data.detail); }
            } catch (e) { alert('Error: ' + e.message); }
            finally { btn.innerText = orig; btn.disabled = false; }
        };
"""

files = ['ai_summary.html', 'trading.html', 'options.html', 'admin.html', 'dashboard.html']
for filename in files:
    f = 'ACTIVE/Insight_Engine/frontend_native/' + filename
    with open(f, 'r') as file:
        content = file.read()
    
    if 'window.changePassword = async () => {' not in content:
        # Clean up old window.updateProfile logic if any
        import re
        content = re.sub(r'window\.updateProfile = async \(\) => \{[\s\S]*?\};', '', content)
        content = re.sub(r'window\.toggleEditProfile = \(edit\) => \{[\s\S]*?\};', '', content)
        
        # Inject new logic
        content = content.replace('</script>\n</body>', js_code + '\n    </script>\n</body>')
        
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated Logic in {f}")

