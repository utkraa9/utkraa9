import argparse, json, math, urllib.request, collections
from pathlib import Path

def draw(data, output_base, title):
    output_base = Path(output_base)
    axes = data["axes"]
    if len(axes) < 3:
        # A radar is not meaningful with fewer than three dimensions.
        # Use a compact bar-style SVG instead of a collapsed polygon.
        W, H = 520, max(180, 85 + len(axes) * 55)
        dark = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
            '<rect width="100%" height="100%" rx="18" fill="#0d1117"/>',
            f'<text x="260" y="31" text-anchor="middle" fill="#e6edf3" font-family="Arial" font-size="18" font-weight="700">{title}</text>'
        ]
        light = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
            '<rect width="100%" height="100%" rx="18" fill="#ffffff"/>',
            f'<text x="260" y="31" text-anchor="middle" fill="#24292f" font-family="Arial" font-size="18" font-weight="700">{title}</text>'
        ]
        for i, a in enumerate(axes):
            y = 65 + i * 55
            width = 300 * a["value"] / 100
            for arr, fg, muted, accent in [
                (dark, "#e6edf3", "#30363d", "#39D353"),
                (light, "#24292f", "#d0d7de", "#1f883d")
            ]:
                arr.append(f'<text x="30" y="{y}" fill="{fg}" font-family="Arial" font-size="13">{a["label"]}</text>')
                arr.append(f'<rect x="130" y="{y-13}" width="300" height="12" rx="6" fill="{muted}"/>')
                arr.append(f'<rect x="130" y="{y-13}" width="{width:.1f}" height="12" rx="6" fill="{accent}"/>')
                arr.append(f'<text x="445" y="{y}" fill="{fg}" font-family="Arial" font-size="12">{a["value"]}%</text>')
        dark.append("</svg>")
        light.append("</svg>")
        (output_base.parent / f"{output_base.name}-dark.svg").write_text("\n".join(dark), encoding="utf-8")
        (output_base.parent / f"{output_base.name}-light.svg").write_text("\n".join(light), encoding="utf-8")
        return

    n = len(axes)
    W = H = 520
    cx = cy = 260
    R = 165

    for theme in ("dark", "light"):
        bg = "#0d1117" if theme == "dark" else "#ffffff"
        fg = "#e6edf3" if theme == "dark" else "#24292f"
        grid = "#30363d" if theme == "dark" else "#d0d7de"
        accent = "#39D353" if theme == "dark" else "#1f883d"

        def ring_points(radius):
            return [
                (cx + radius * math.cos(-math.pi/2 + i*2*math.pi/n),
                 cy + radius * math.sin(-math.pi/2 + i*2*math.pi/n))
                for i in range(n)
            ]

        points = [
            (cx + R * a["value"]/100 * math.cos(-math.pi/2 + i*2*math.pi/n),
             cy + R * a["value"]/100 * math.sin(-math.pi/2 + i*2*math.pi/n))
            for i, a in enumerate(axes)
        ]

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            f'<rect width="100%" height="100%" rx="18" fill="{bg}"/>',
            f'<text x="{cx}" y="31" text-anchor="middle" fill="{fg}" font-family="Arial" font-size="18" font-weight="700">{title}</text>'
        ]

        for level in (25, 50, 75, 100):
            pts = ring_points(R * level / 100)
            svg.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{grid}"/>')

        for i, axis in enumerate(axes):
            ang = -math.pi/2 + i*2*math.pi/n
            x2, y2 = cx + R*math.cos(ang), cy + R*math.sin(ang)
            tx, ty = cx + (R+27)*math.cos(ang), cy + (R+27)*math.sin(ang)
            anchor = "middle" if abs(math.cos(ang)) < .25 else ("start" if math.cos(ang) > 0 else "end")
            svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{grid}"/>')
            svg.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" fill="{fg}" font-family="Arial" font-size="12">{axis["label"]}</text>')

        svg.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}" fill="{accent}" fill-opacity=".20" stroke="{accent}" stroke-width="2"/>')
        for x, y in points:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{accent}"/>')
        svg.append("</svg>")
        (output_base.parent / f"{output_base.name}-{theme}.svg").write_text("\n".join(svg), encoding="utf-8")

def github_languages(username, output_base, limit=7):
    req = urllib.request.Request(
        f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated",
        headers={"Accept":"application/vnd.github+json","User-Agent":"utkraa9-profile"}
    )
    repos = json.load(urllib.request.urlopen(req, timeout=20))
    counts = collections.Counter(r.get("language") for r in repos if r.get("language"))
    top = counts.most_common(limit)
    total = sum(v for _, v in top) or 1
    axes = [{"label": lang, "value": round(count/total*100)} for lang, count in top]
    if not axes:
        axes = [{"label":"No language data", "value":0}]
    draw({"axes": axes}, output_base, "GitHub Languages")

p = argparse.ArgumentParser()
p.add_argument("--data")
p.add_argument("-o", "--output", default="assets/radar")
p.add_argument("--github")
p.add_argument("--limit", type=int, default=7)
a = p.parse_args()

if a.data:
    d = json.load(open(a.data, encoding="utf-8"))
    draw(d, a.output, d.get("title", "Skill Radar"))
elif a.github:
    github_languages(a.github, a.output, a.limit)
