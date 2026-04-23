import os
import glob

html_files = glob.glob('ACTIVE/Insight_Engine/frontend_native/*.html')

manifest_tag = '<link rel="manifest" href="manifest.json">'
sw_script = """
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('sw.js')
                    .then(reg => console.log('SW Registered', reg))
                    .catch(err => console.log('SW Failed', err));
            });
        }
    </script>
</body>
"""

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject manifest
    if 'manifest.json' not in content:
        content = content.replace('</head>', f'    {manifest_tag}\n</head>')

    # Inject Service Worker
    if 'serviceWorker.register' not in content:
        content = content.replace('</body>', sw_script)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("PWA elements injected successfully!")
