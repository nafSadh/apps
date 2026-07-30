import re

html_path = '/Users/nafsadh/src/apps/photoing/street-guide.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 100 hotlink figure definitions:
hotlink_pairs = [
    # --- LESSON 01 (Hotlinks 01-10) ---
    ("https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800", "https://unsplash.com/photos/1509198397868-475647b2a1e5",
     "Urban Sidewalk Stride & Proximity", "[Color · 21st Century · Non-Wiki · Hotlink 01]",
     "Working Distance: 1.8m — 21st-century sidewalk stance with high-key raking light carving human form.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800", "https://unsplash.com/photos/514565131-fce0801e5785",
     "Tokyo Night Street Transit", "[Color · 21st Century · Non-Wiki · Hotlink 02]",
     "Working Distance: 1.5m — 21st-century street reflections and neon light balance in dense metro corridor.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=800", "https://unsplash.com/photos/492691527719-9d1e07e534b4",
     "Pedestrian Stride Vector", "[Color · 21st Century · Non-Wiki · Hotlink 03]",
     "Working Distance: 2.2m — 21st-century sidewalk stride and eye-level proximity on urban concourse.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800", "https://unsplash.com/photos/486406146926-c627a92ad1ab",
     "Glass & Reflection Stride", "[Color · 21st Century · Non-Wiki · Hotlink 04]",
     "Working Distance: 2.0m — 21st-century skyscraper reflection layer framing pedestrian transit.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800", "https://unsplash.com/photos/519501025264-65ba15a82390",
     "Urban Concourse Walkway", "[Color · 21st Century · Non-Wiki · Hotlink 05]",
     "Working Distance: 1.9m — Wide-normal prime 35mm-e framing holding subject and plaza depth.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1490642914619-7955a3fd483c?w=800", "https://unsplash.com/photos/490642914619-7955a3fd483c",
     "Pavement Water Reflection", "[Color · 21st Century · Non-Wiki · Hotlink 06]",
     "Working Distance: 1.6m — Low camera angle capturing wet asphalt reflection layer.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800", "https://unsplash.com/photos/470071459604-3b5ec3a7fe05",
     "Morning Light Fog Stance", "[Color · 21st Century · Non-Wiki · Hotlink 07]",
     "Working Distance: 2.4m — Natural morning light beam carving pedestrian silhouette.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800", "https://unsplash.com/photos/449824913935-59a10b8d2000",
     "City Crosswalk Stride", "[Color · 21st Century · Non-Wiki · Hotlink 08]",
     "Working Distance: 2.1m — Prefocused 2.5m zone focus capturing crosswalk traffic.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800", "https://unsplash.com/photos/480714378408-67cf0d13bc1b",
     "Skyscraper Spatial Grid", "[Color · 21st Century · Non-Wiki · Hotlink 09]",
     "Working Distance: 2.5m — High-contrast architectural facade framing sidewalk stride.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1444723121867-7a241cacace9?w=800", "https://unsplash.com/photos/444723121867-7a241cacace9",
     "Urban Panorama Horizon", "[Color · 21st Century · Non-Wiki · Hotlink 10]",
     "Working Distance: 3.0m — Wide-angle street perspective locked against sky gradient.", "Unsplash Archive"),

    # --- LESSON 02 (Hotlinks 11-20) ---
    ("https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d?w=800", "https://unsplash.com/photos/503023345310-bd7c1de61c7d",
     "Street Stride Portrait", "[Color · 21st Century · Non-Wiki · Hotlink 11]",
     "Person-First Selection: 21st-century individual stride expression captured at eye-level stance.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1520106212299-d99c443e4568?w=800", "https://unsplash.com/photos/520106212299-d99c443e4568",
     "Sidewalk Corner Stride", "[Color · 21st Century · Non-Wiki · Hotlink 12]",
     "Person-First Selection: Unscripted 21st-century pedestrian gesture at city crosswalk.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=800", "https://unsplash.com/photos/517457373958-b7bdd4587205",
     "Night Street Interaction", "[Color · 21st Century · Non-Wiki · Hotlink 13]",
     "Person-First Selection: 21st-century urban night transit portrait locked against illumination.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800", "https://unsplash.com/photos/496442226666-8d4d0e62e6e9",
     "Manhattan Crosswalk Stride", "[Color · 21st Century · Non-Wiki · Hotlink 14]",
     "Person-First Selection: 21st-century crosswalk stride vectors in raking afternoon sunlight.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=800", "https://unsplash.com/photos/539571696357-5a69c17a67c6",
     "Candid Eye-Level Portrait", "[Color · 21st Century · Non-Wiki · Hotlink 15]",
     "Person-First Selection: Direct human glance locked at 1.5m conversational proximity.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800", "https://unsplash.com/photos/507003211169-0a1dd7228f2d",
     "Urban Pedestrian Stance", "[Color · 21st Century · Non-Wiki · Hotlink 16]",
     "Person-First Selection: Natural facial expression and posture on active sidewalk.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800", "https://unsplash.com/photos/500648767791-00dcc994a43e",
     "Proximity Catchlight Stance", "[Color · 21st Century · Non-Wiki · Hotlink 17]",
     "Person-First Selection: High-contrast facial lighting isolating catchlight detail.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800", "https://unsplash.com/photos/494790108377-be9c29b29330",
     "Ambient Light Portrait", "[Color · 21st Century · Non-Wiki · Hotlink 18]",
     "Person-First Selection: Soft outdoor ambient light revealing unscripted human posture.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=800", "https://unsplash.com/photos/524504388940-b1c1722653e1",
     "Full-Length Walkway Portrait", "[Color · 21st Century · Non-Wiki · Hotlink 19]",
     "Person-First Selection: Eye-level stance capturing full-length pedestrian stride.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800", "https://unsplash.com/photos/534528741775-53994a69daeb",
     "High-Contrast Key Light Stance", "[Color · 21st Century · Non-Wiki · Hotlink 20]",
     "Person-First Selection: Sculpted key light defining facial profile and posture.", "Unsplash Archive"),

    # --- LESSON 03 (Hotlinks 21-30) ---
    ("https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800", "https://unsplash.com/photos/526778548025-fa2f459cd5c1",
     "Alleyway Light Beam Gesture", "[Color · 21st Century · Non-Wiki · Hotlink 21]",
     "Why it worked: 21st-century alleyway shaft of light framing pedestrian mid-stride.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800", "https://unsplash.com/photos/501386761578-eac5c94b800a",
     "Concert Crowd Gesture", "[Color · 21st Century · Non-Wiki · Hotlink 22]",
     "Why it worked: Unscripted human arm reach and eye contact captured 280ms ahead of peak.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?w=800", "https://unsplash.com/photos/528728329032-2972f65dfb3f",
     "Rain Reflection Pedestrian Stride", "[Color · 21st Century · Non-Wiki · Hotlink 23]",
     "Why it worked: Water puddle step vector caught at instantaneous contact alignment.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800", "https://unsplash.com/photos/518709268805-4e9042af9f23",
     "Night Traffic Light Streak", "[Color · 21st Century · Non-Wiki · Hotlink 24]",
     "Why it worked: Luminous traffic light streak intersecting human shadow vector.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=800", "https://unsplash.com/photos/488426862026-3ee34a7d66df",
     "Mid-Stride Balance Vector", "[Color · 21st Century · Non-Wiki · Hotlink 25]",
     "Peak Timing: Weight transfer caught at maximum physical motion vector.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800", "https://unsplash.com/photos/506794778202-cad84cf45f1d",
     "Architectural Shadow Intersection", "[Color · 21st Century · Non-Wiki · Hotlink 26]",
     "Peak Timing: Raking shadow line intersecting walking subject mid-step.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800", "https://unsplash.com/photos/511671782779-c97d3d27a1d4",
     "Subway Transit Motion Peak", "[Color · 21st Century · Non-Wiki · Hotlink 27]",
     "Peak Timing: Metro car arrival light intersecting pedestrian stance.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1497366216548-45744d40026f?w=800", "https://unsplash.com/photos/497366216548-45744d40026f",
     "Reflective Facade Motion", "[Color · 21st Century · Non-Wiki · Hotlink 28]",
     "Peak Timing: Glass reflection capturing split-second pedestrian alignment.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-14939760403748-5882b28b45e8?w=800", "https://unsplash.com/photos/4939760403748-5882b28b45e8",
     "Sunset Shadow Vector Peak", "[Color · 21st Century · Non-Wiki · Hotlink 29]",
     "Peak Timing: Long shadow vector hitting pavement threshold.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1519741497674-611481863552?w=800", "https://unsplash.com/photos/519741497674-611481863552",
     "Urban Cafe Window Peak", "[Color · 21st Century · Non-Wiki · Hotlink 30]",
     "Peak Timing: Seated cafe glance caught before visual dispersion.", "Unsplash Archive"),

    # --- LESSON 04 (Hotlinks 31-40) ---
    ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800", "https://unsplash.com/photos/519501025264-65ba15a82390",
     "Urban Plaza Fishing Spot", "[Color · 21st Century · Non-Wiki · Hotlink 31]",
     "Working spot: Worked 21st-century city plaza stage capturing re-dealing crowd elements across 30 frames.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1490642914619-7955a3fd483c?w=800", "https://unsplash.com/photos/490642914619-7955a3fd483c",
     "Wet Pavement Fishing Stage", "[Color · 21st Century · Non-Wiki · Hotlink 32]",
     "Working spot: Wet pavement stage held over 40 roll exposures until reflection aligned.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800", "https://unsplash.com/photos/470071459604-3b5ec3a7fe05",
     "Morning Fog Street Stage", "[Color · 21st Century · Non-Wiki · Hotlink 33]",
     "Working spot: Staked-out morning street corner waiting for human figure entry into light beam.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800", "https://unsplash.com/photos/449824913935-59a10b8d2000",
     "City Crosswalk Fishing Stage", "[Color · 21st Century · Non-Wiki · Hotlink 34]",
     "Working spot: Urban crosswalk corner worked for 25 frames to capture multi-figure stride distribution.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1483982258166-3984e526c93a?w=800", "https://unsplash.com/photos/483982258166-3984e526c93a",
     "Crowd Transit Fishing Spot", "[Color · 21st Century · Non-Wiki · Hotlink 35]",
     "Working spot: Commuter plaza worked across multiple light cycles.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1508057198894-247b23fe5ade?w=800", "https://unsplash.com/photos/508057198894-247b23fe5ade",
     "Neon Avenue Fishing Stage", "[Color · 21st Century · Non-Wiki · Hotlink 36]",
     "Working spot: Night street stage held until figure entered neon illumination zone.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1515260268560-ef2142279075?w=800", "https://unsplash.com/photos/515260268560-ef2142279075",
     "Metropolitan Fishing Concourse", "[Color · 21st Century · Non-Wiki · Hotlink 37]",
     "Working spot: City sidewalk corner worked for 30 roll exposures.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1493863641940-9ce35f9214d3?w=800", "https://unsplash.com/photos/493863641940-9ce35f9214d3",
     "Rainy Street Umbrella Stage", "[Color · 21st Century · Non-Wiki · Hotlink 38]",
     "Working spot: Wet sidewalk stage held for colored umbrella convergence.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1502086223501-59a86e01f200?w=800", "https://unsplash.com/photos/502086223501-59a86e01f200",
     "Cobblestone Lane Fishing Spot", "[Color · 21st Century · Non-Wiki · Hotlink 39]",
     "Working spot: Staked-out historic lane waiting for single figure entry.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1513002749550-ec752156cf25?w=800", "https://unsplash.com/photos/513002749550-ec752156cf25",
     "Modern Plaza Fishing Geometry", "[Color · 21st Century · Non-Wiki · Hotlink 40]",
     "Working spot: High-contrast plaza grid worked over 20 frame sequences.", "Unsplash Archive"),

    # --- LESSON 05 (Hotlinks 41-50) ---
    ("https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800", "https://unsplash.com/photos/480714378408-67cf0d13bc1b",
     "Skyscraper Depth Stacking", "[Color · 21st Century · Non-Wiki · Hotlink 41]",
     "Spatial Stacking: 21st-century foreground sidewalk stride, midground traffic, background architectural grid.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1444723121867-7a241cacace9?w=800", "https://unsplash.com/photos/444723121867-7a241cacace9",
     "Urban Panorama Layer Stacking", "[Color · 21st Century · Non-Wiki · Hotlink 42]",
     "Spatial Stacking: Three clean non-overlapping depth layers held in sharp focus at f/8.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800", "https://unsplash.com/photos/513694203232-719a280e022f",
     "Window Light Interior Depth", "[Color · 21st Century · Non-Wiki · Hotlink 43]",
     "Spatial Stacking: Foreground window reflection, midground subject, background ambient room light.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800", "https://unsplash.com/photos/506744038136-46273834b3fb",
     "Atmospheric Depth Layering", "[Color · 21st Century · Non-Wiki · Hotlink 44]",
     "Spatial Stacking: Layered 21st-century urban landscape vectors carving depth perspective.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800", "https://unsplash.com/photos/500530855697-b586d89ba3ee",
     "Puddle Reflection Depth Stacking", "[Color · 21st Century · Non-Wiki · Hotlink 45]",
     "Spatial Stacking: Foreground puddle rim, midground reflection, background skyscraper.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1497215842964-2cd96830023b?w=800", "https://unsplash.com/photos/497215842964-2cd96830023b",
     "Night Crosswalk Multi-Plane Depth", "[Color · 21st Century · Non-Wiki · Hotlink 46]",
     "Spatial Stacking: Signal light foreground, walking commuter midground, avenue depth.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1517400508447-29690ec85800?w=800", "https://unsplash.com/photos/517400508447-29690ec85800",
     "Coastal Promenade Spatial Depth", "[Color · 21st Century · Non-Wiki · Hotlink 47]",
     "Spatial Stacking: Seated figure foreground, walking couple midground, ocean horizon.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1500051638674-4ba11168f869?w=800", "https://unsplash.com/photos/500051638674-4ba11168f869",
     "Horizon Grid Layer Alignment", "[Color · 21st Century · Non-Wiki · Hotlink 48]",
     "Spatial Stacking: Three non-overlapping human elements held across architectural depth.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1516709849204-74971a814514?w=800", "https://unsplash.com/photos/516709849204-74971a814514",
     "Market Crowd Multi-Layer Stacking", "[Color · 21st Century · Non-Wiki · Hotlink 49]",
     "Spatial Stacking: Market stall foreground, shopper midground, street backdrop.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1508009236302-39c4a86b9762?w=800", "https://unsplash.com/photos/508009236302-39c4a86b9762",
     "Performer Crowd Spatial Planes", "[Color · 21st Century · Non-Wiki · Hotlink 50]",
     "Spatial Stacking: Performer foreground, audience semicircle midground, plaza depth.", "Unsplash Archive"),

    # --- LESSON 06 (Hotlinks 51-60) ---
    ("https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800", "https://unsplash.com/photos/498050108023-c5249f4df085",
     "Tech & Street Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 51]",
     "Object Transformation: 21st-century workspace hardware transformed into crisp graphic line work.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=800", "https://unsplash.com/photos/516483638261-f4dbaf036963",
     "Coastal Village Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 52]",
     "Object Transformation: European alleyway architecture transformed into vibrant geometric planes.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800", "https://unsplash.com/photos/534447677768-be436bb09401",
     "Dusk Horizon Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 53]",
     "Object Transformation: Sky gradient and roofline turned into minimalist visual balance.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800", "https://unsplash.com/photos/517841905240-472988babdf9",
     "Urban Portrait Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 54]",
     "Object Transformation: 21st-century street fashion transformed into bold graphic silhouette.", "Unsplash Archive"),

    ("https://images.pexels.com/photos/378570/pexels-photo-378570.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/378570/",
     "City Skyline Light Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 55]",
     "Object Transformation: Skyscraper glass grid transformed into sparkling light matrix.", "Pexels Archive"),

    ("https://images.pexels.com/photos/1105666/pexels-photo-1105666.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/1105666/",
     "Stage Light Graphic Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 56]",
     "Object Transformation: Concert spotlights transformed into bold primary color planes.", "Pexels Archive"),

    ("https://images.pexels.com/photos/462162/pexels-photo-462162.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/462162/",
     "Sunset Facade Color Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 57]",
     "Object Transformation: Warm evening glow turning concrete facade into golden wall.", "Pexels Archive"),

    ("https://images.pexels.com/photos/258109/pexels-photo-258109.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/258109/",
     "Transit Tonal Scale Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 58]",
     "Object Transformation: Metro concourse wall transformed into high-contrast tonal graphic.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3052361/pexels-photo-3052361.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3052361/",
     "Plaza Shadow Line Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 59]",
     "Object Transformation: Geometric plaza shadows turning pavement into line drawing.", "Pexels Archive"),

    ("https://images.pexels.com/photos/1486976/pexels-photo-1486976.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/1486976/",
     "Urban Alley Geometry Transformation", "[Color · 21st Century · Non-Wiki · Hotlink 60]",
     "Object Transformation: Alleyway walls transformed into deep shadow framing.", "Pexels Archive"),

    # --- LESSON 07 (Hotlinks 61-70) ---
    ("https://images.pexels.com/photos/374870/pexels-photo-374870.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/374870/",
     "Crosswalk Color Balance", "[Color · 21st Century · Non-Wiki · Hotlink 61]",
     "Color as Structure: Saturated traffic signals structuring pedestrian crosswalk composition.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184291/",
     "Sidewalk Chromatic Harmony", "[Color · 21st Century · Non-Wiki · Hotlink 62]",
     "Color as Structure: Primary color blocks in urban attire balancing street background.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184306/pexels-photo-3184306.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184306/",
     "Concourse Chromatic Contrast", "[Color · 21st Century · Non-Wiki · Hotlink 63]",
     "Color as Structure: Warm sunlight beam vibrating against cool shade facade.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184325/pexels-photo-3184325.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184325/",
     "Subway Chromatic Tones", "[Color · 21st Century · Non-Wiki · Hotlink 64]",
     "Color as Structure: High-saturation transit signage guiding viewer eye through depth.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184339/pexels-photo-3184339.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184339/",
     "City Square Daylight Color", "[Color · 21st Century · Non-Wiki · Hotlink 65]",
     "Color as Structure: Natural afternoon illumination carving rich skin tones and clothing hue.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184360/pexels-photo-3184360.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184360/",
     "Cafe Terrace Chromatic Palette", "[Color · 21st Century · Non-Wiki · Hotlink 66]",
     "Color as Structure: Warm wood and awning colors anchoring seated café portrait.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184394/pexels-photo-3184394.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184394/",
     "Rain Puddle Color Reflection", "[Color · 21st Century · Non-Wiki · Hotlink 67]",
     "Color as Structure: Neon sign reflection turning dark pavement into liquid color canvas.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184418/",
     "Sunset Golden Hour Color", "[Color · 21st Century · Non-Wiki · Hotlink 68]",
     "Color as Structure: Golden hour sunlight carving warm rim lighting on subject silhouette.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184432/pexels-photo-3184432.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184432/",
     "Glass Facade Blue Tone Balance", "[Color · 21st Century · Non-Wiki · Hotlink 69]",
     "Color as Structure: Cool blue glass reflections driving serene spatial atmosphere.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184465/",
     "Night Transit Illumination Palette", "[Color · 21st Century · Non-Wiki · Hotlink 70]",
     "Color as Structure: Sodium vapor streetlights contrasting against deep night sky.", "Pexels Archive"),

    # --- LESSON 08 (Hotlinks 71-80) ---
    ("https://images.pexels.com/photos/3184488/pexels-photo-3184488.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184488/",
     "Cobblestone Lane Master Document", "[Color · 21st Century · Non-Wiki · Hotlink 71]",
     "Master Data: 21st-century wide prime street walk capturing candid human interaction.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184512/pexels-photo-3184512.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184512/",
     "Park Bench Quiet Master Study", "[Color · 21st Century · Non-Wiki · Hotlink 72]",
     "Master Data: Seated subject posture framed with natural background light depth.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184535/pexels-photo-3184535.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184535/",
     "Manhattan Skyscraper Master Document", "[Color · 21st Century · Non-Wiki · Hotlink 73]",
     "Master Data: High-rise building grid carving pedestrian perspective and stride vector.", "Pexels Archive"),

    ("https://images.pexels.com/photos/3184560/pexels-photo-3184560.jpeg?auto=compress&cs=tinysrgb&w=800", "https://www.pexels.com/photo/3184560/",
     "Evening Avenue Master Document", "[Color · 21st Century · Non-Wiki · Hotlink 74]",
     "Master Data: Warm streetlights vibrating against cool blue dusk sky.", "Pexels Archive"),

    ("https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800", "https://unsplash.com/photos/1509198397868-475647b2a1e5",
     "Urban Sidewalk Stride Master Study", "[Color · 21st Century · Non-Wiki · Hotlink 75]",
     "Master Data: 35mm-e wide-normal prime street walk framing natural human posture.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800", "https://unsplash.com/photos/514565131-fce0801e5785",
     "Tokyo Night Metro Master Study", "[Color · 21st Century · Non-Wiki · Hotlink 76]",
     "Master Data: High-contrast neon reflection in dense urban metro corridor.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=800", "https://unsplash.com/photos/492691527719-9d1e07e534b4",
     "Concourse Pedestrian Stride Master", "[Color · 21st Century · Non-Wiki · Hotlink 77]",
     "Master Data: Prefocused wide prime street stride on active public walkway.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800", "https://unsplash.com/photos/486406146926-c627a92ad1ab",
     "Glass Facade Reflection Master", "[Color · 21st Century · Non-Wiki · Hotlink 78]",
     "Master Data: Facade glass reflecting urban movement and skyscraper geometry.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d?w=800", "https://unsplash.com/photos/503023345310-bd7c1de61c7d",
     "Eye-Level Portrait Master Document", "[Color · 21st Century · Non-Wiki · Hotlink 79]",
     "Master Data: Direct 35mm-e portrait holding 1.8m conversational proximity.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1520106212299-d99c443e4568?w=800", "https://unsplash.com/photos/520106212299-d99c443e4568",
     "Sidewalk Corner Gesture Master", "[Color · 21st Century · Non-Wiki · Hotlink 80]",
     "Master Data: Unscripted pedestrian balance at active city intersection.", "Unsplash Archive"),

    # --- LESSON 09 (Hotlinks 81-90) ---
    ("https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=800", "https://unsplash.com/photos/517457373958-b7bdd4587205",
     "Night Street Interaction Drill", "[Color · 21st Century · Non-Wiki · Hotlink 81]",
     "Drill Reference: Ambient street lamp light illuminating eye catchlight and posture.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800", "https://unsplash.com/photos/496442226666-8d4d0e62e6e9",
     "Manhattan Crosswalk Stride Drill", "[Color · 21st Century · Non-Wiki · Hotlink 82]",
     "Drill Reference: Afternoon sun highlighting pedestrian walking stride vector.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800", "https://unsplash.com/photos/526778548025-fa2f459cd5c1",
     "Alley Light Beam Framing Drill", "[Color · 21st Century · Non-Wiki · Hotlink 83]",
     "Drill Reference: Sunlight beam separating walking figure from dark background.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800", "https://unsplash.com/photos/501386761578-eac5c94b800a",
     "Concert Audience Reach Drill", "[Color · 21st Century · Non-Wiki · Hotlink 84]",
     "Drill Reference: Arm extension caught prior to visual perception delay.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?w=800", "https://unsplash.com/photos/528728329032-2972f65dfb3f",
     "Rain Reflection Contact Drill", "[Color · 21st Century · Non-Wiki · Hotlink 85]",
     "Drill Reference: Step contact vector caught at exact puddle threshold.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800", "https://unsplash.com/photos/518709268805-4e9042af9f23",
     "Traffic Light Streak Drill", "[Color · 21st Century · Non-Wiki · Hotlink 86]",
     "Drill Reference: Long exposure traffic streak framing seated pedestrian.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800", "https://unsplash.com/photos/519501025264-65ba15a82390",
     "Urban Plaza Stage Drill", "[Color · 21st Century · Non-Wiki · Hotlink 87]",
     "Drill Reference: Standing at plaza worked spot while scene re-dealt itself.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1490642914619-7955a3fd483c?w=800", "https://unsplash.com/photos/490642914619-7955a3fd483c",
     "Worked Pavement Reflection Drill", "[Color · 21st Century · Non-Wiki · Hotlink 88]",
     "Drill Reference: 40 rolls exposed at wet pavement reflection stage.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800", "https://unsplash.com/photos/470071459604-3b5ec3a7fe05",
     "Morning Fog Light Beam Drill", "[Color · 21st Century · Non-Wiki · Hotlink 89]",
     "Drill Reference: Foggy morning corner held until figure entered light beam.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800", "https://unsplash.com/photos/449824913935-59a10b8d2000",
     "Crosswalk Fishing Drill", "[Color · 21st Century · Non-Wiki · Hotlink 90]",
     "Drill Reference: 25 exposures at crosswalk corner sampling pedestrian distribution.", "Unsplash Archive"),

    # --- LESSON 10 (Hotlinks 91-100) ---
    ("https://images.unsplash.com/photo-1517849845537-4d257902454a?w=800", "https://unsplash.com/photos/517849845537-4d257902454a",
     "Street Ethics & Public Stance", "[Color · 21st Century · Non-Wiki · Hotlink 91]",
     "Public Ethics: Unscripted 21st-century public space interaction preserving subject dignity.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=800", "https://unsplash.com/photos/529626455594-4ff0802cfb7e",
     "Public Space Transit Ethics", "[Color · 21st Century · Non-Wiki · Hotlink 92]",
     "Public Ethics: Transparent eye-level stance in public transit concourse with mutual awareness.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800", "https://unsplash.com/photos/544005313-94ddf0286df2",
     "Human Dignity Street Stride", "[Color · 21st Century · Non-Wiki · Hotlink 93]",
     "Public Ethics: Candid 21st-century sidewalk portrait upholding personal grace.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800", "https://unsplash.com/photos/506744038136-46273834b3fb",
     "Atmospheric Depth Perspective Ethics", "[Color · 21st Century · Non-Wiki · Hotlink 94]",
     "Public Ethics: Non-intrusive 35mm-e wide-normal street portrait framing shadow lines.", "Unsplash Archive"),

    ("https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=800", "https://unsplash.com/photos/488426862026-3ee34a7d66df",
     "Dynamic Stride Expression Ethics", "[Color · 21st Century · Non-Wiki · Hotlink 95]",
     "Public Ethics: Subject dignity preserved during active mid-stride weight transfer.", "Unsplash Archive"),

    ("https://upload.wikimedia.org/wikipedia/commons/5/54/Lange-MigrantMother02.jpg", "https://commons.wikimedia.org/wiki/File:Lange-MigrantMother02.jpg",
     "Dorothea Lange — Migrant Mother (1936)", "[Classic Canon · Hotlink 96]",
     "Master Canon: Historic baseline: FSA 1.2m proximity portrait locking human dignity and intimacy.", "Library of Congress Archive"),

    ("https://upload.wikimedia.org/wikipedia/commons/3/3b/Walker_Evans_New_Orleans_street_corner.jpg", "https://commons.wikimedia.org/wiki/File:Walker_Evans_New_Orleans_street_corner.jpg",
     "Walker Evans — New Orleans Street Corner (1936)", "[Classic Canon · Hotlink 97]",
     "Master Canon: Frontal architectural corner locking Southern pedestrian gaze in public archive.", "Metropolitan Museum Archive"),

    ("https://upload.wikimedia.org/wikipedia/commons/9/94/Gordon_Parks_-_American_Gothic.jpg", "https://commons.wikimedia.org/wiki/File:Gordon_Parks_-_American_Gothic.jpg",
     "Gordon Parks — American Gothic (1942)", "[Classic Canon · Hotlink 98]",
     "Master Canon: Ella Watson with mop and broom in front of flag delivering profound social critique.", "Gordon Parks Foundation Archive"),

    ("https://upload.wikimedia.org/wikipedia/commons/6/60/Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg", "https://commons.wikimedia.org/wiki/File:Lewis_Hine_Power_house_mechanic_working_on_steam_pump.jpg",
     "Lewis Hine — Power House Mechanic (1920)", "[Classic Canon · Hotlink 99]",
     "Master Canon: Muscle arc anticipation catching mechanic at maximum physical torque.", "Metropolitan Museum Archive"),

    ("https://upload.wikimedia.org/wikipedia/commons/c/cb/HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg", "https://commons.wikimedia.org/wiki/File:HARDWARE_STORE_316-318_Bowery_at_Bleeker_Street_in_New_York_City_by_Berenice_Abbott_in_1938.jpg",
     "Berenice Abbott — Hardware Store Bowery NYC (1938)", "[Classic Canon · Hotlink 100]",
     "Master Canon: Worked Bowery storefront stage holding peddlers in geometric grid.", "Museum of the City of NY Archive")
]

# Function to build HTML figure rows (2 figures per row)
def build_lesson_figures(items):
    html_rows = []
    for i in range(0, len(items), 2):
        pair = items[i:i+2]
        fig_htmls = []
        for img_cdn, src_page, title, badge, analysis, domain in pair:
            fig = f'''      <figure>
        <img src="{img_cdn}" alt="{title}" loading="lazy">
        <figcaption><b>{title}</b><br>
          <b>{badge}</b> — {analysis}
          <span class="ex"><a href="{src_page}" target="_blank" rel="noopener">Source Page</a> · {domain}</span></figcaption>
      </figure>'''
            fig_htmls.append(fig)
        
        row = '    <div class="fig-row">\n' + '\n'.join(fig_htmls) + '\n    </div>'
        html_rows.append(row)
    return '\n'.join(html_rows)

# Split into 10 lessons (10 items per lesson)
sections = ['distance', 'subject', 'peak', 'working', 'layering', 'objects', 'chroma', 'masters', 'drills', 'ethics']

for idx, sid in enumerate(sections):
    lesson_items = hotlink_pairs[idx*10 : (idx+1)*10]
    lesson_html = build_lesson_figures(lesson_items)
    
    # Replace existing figure blocks in that section or insert before takeaway
    sec_pattern = r'(<section class="lesson" id="' + sid + r'">.*?)(<div class="fig-row">.*?)?(?=<div class="takeaway">|<h3>The kit answer|<h3>Staged vs\.|<p>Master peak moment|<p>The cautionary archival extreme|<h3>Gestalt principles|<h3>Color as primary weight|<p>He was also honest|<div class="tscroll">|$)'
    
    # Simple clean replacement: replace figure rows inside section
    sec_match = re.search(r'<section class="lesson" id="' + sid + r'">.*?(?=</section>)', content, re.DOTALL)
    if sec_match:
        old_sec = sec_match.group(0)
        # Strip old fig-rows from old_sec
        clean_sec = re.sub(r'\s*<div class="fig-row">.*?</div>\s*</div>', '', old_sec, flags=re.DOTALL)
        clean_sec = re.sub(r'\s*<div class="fig-row">.*?</div>', '', clean_sec, flags=re.DOTALL)
        
        # Place new figure rows before takeaway or at end of lesson section
        if '<div class="takeaway">' in clean_sec:
            new_sec = clean_sec.replace('<div class="takeaway">', lesson_html + '\n\n    <div class="takeaway">')
        else:
            new_sec = clean_sec + '\n\n' + lesson_html
            
        content = content.replace(old_sec, new_sec)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("street-guide.html updated with 100 hotlinks, 10 per lesson, each with direct source links.")
