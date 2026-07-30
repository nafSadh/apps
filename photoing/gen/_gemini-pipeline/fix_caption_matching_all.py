import re

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix pexels-photo-1105666 figure title and description across street-guide.html:
# Old title: "Manhattan Crosswalk Afternoon Raking Sunlight"
# New title: "Live Concert Audience & Raised Arm Gesture Silhouette"
# New analysis: "Public Gathering Gesture: High-voltage stage lighting carving silhouetted arm gestures across a crowded venue concourse."

content = re.sub(
    r'<img src="https://images\.pexels\.com/photos/1105666/pexels-photo-1105666\.jpeg[^"]*" alt="[^"]*" loading="lazy">\s*<figcaption><b>[^<]*</b><br>\s*<b>([^<]*)</b> — [^<]*',
    r'<img src="https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg?auto=compress&cs=tinysrgb&w=800" alt="Live Concert Audience & Raised Arm Gesture Silhouette" loading="lazy">\n        <figcaption><b>Live Concert Audience & Raised Arm Gesture Silhouette</b><br>\n          <b>\1</b> — Public Gathering Gesture: High-voltage stage lighting carving silhouetted arm gestures across a crowded venue concourse.',
    content
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("street-guide.html updated successfully: pexels-photo-1105666 correctly titled 'Live Concert Audience & Raised Arm Gesture Silhouette'.")
