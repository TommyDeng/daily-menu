import hashlib
import hmac
from datetime import date
from html import escape
from http.cookies import SimpleCookie
from urllib.parse import urlparse

from workers import Response, WorkerEntrypoint


PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f4efe6">
<title>__TITLE__</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23c6532a'/%3E%3Ctext x='32' y='44' text-anchor='middle' font-size='34' fill='%23fffaf3' font-family='serif'%3E食%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&family=Noto+Serif+SC:wght@600;700&display=swap" rel="stylesheet">
<style>
:root {
    --paper: #f3eee4;
    --card: #fffaf3;
    --ink: #241c15;
    --muted: #7d7268;
    --line: rgba(62, 44, 26, 0.12);
    --chili: #c6532a;
    --chili-deep: #8d3416;
    --sage: #3d6848;
    --shadow: 0 16px 40px rgba(70, 46, 22, 0.08);
    --serif: "Noto Serif SC", "Songti SC", "STSong", serif;
    --sans: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}
* { box-sizing: border-box; }
html { font-size: 16px; }
body {
    margin: 0;
    min-height: 100dvh;
    color: var(--ink);
    font-family: var(--sans);
    line-height: 1.55;
    background:
        radial-gradient(900px 420px at -10% -10%, #f8dcc8 0%, transparent 58%),
        radial-gradient(700px 380px at 110% -8%, #e7efd8 0%, transparent 52%),
        var(--paper);
}
body.gate {
    display: grid;
    place-items: center;
    padding: 24px 16px;
}
a { color: var(--chili-deep); }
button, input { font: inherit; color: inherit; }
:focus-visible { outline: 2px solid var(--chili); outline-offset: 3px; }
.wrap {
    width: min(680px, calc(100% - 32px));
    margin: 0 auto;
    padding: 22px 0 72px;
}
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 28px;
}
.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--ink);
    text-decoration: none;
    font-family: var(--serif);
    font-weight: 700;
    letter-spacing: 0.02em;
}
.brand-mark {
    width: 36px;
    height: 36px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: var(--chili);
    color: #fffaf3;
    box-shadow: 0 8px 16px rgba(198, 83, 42, 0.25);
}
nav { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; justify-content: flex-end; }
.nav-link {
    color: var(--ink);
    text-decoration: none;
    padding: 0.38rem 0.75rem;
    border-radius: 999px;
    font-size: 0.92rem;
}
.nav-link.is-active { background: var(--ink); color: #f6f1e8; }
.nav-link.quiet { color: var(--muted); }
.eyebrow {
    margin: 0;
    color: var(--chili);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.16em;
}
h1 {
    margin: 0.15rem 0 0.35rem;
    font-family: var(--serif);
    font-weight: 700;
    font-size: clamp(1.9rem, 4vw, 2.5rem);
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.lede { margin: 0 0 22px; color: var(--muted); max-width: 36em; }
.notice {
    margin: 0 0 14px;
    padding: 10px 12px;
    border-radius: 12px;
    background: #fde8df;
    color: var(--chili-deep);
}
.dishes { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.dish {
    position: relative;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    padding: 15px 16px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 18px;
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.7) inset;
    cursor: pointer;
    transition: border-color 160ms ease, transform 160ms ease, background 160ms ease;
}
.dish:hover { border-color: #e4cbbd; transform: translateY(-1px); }
.dish input {
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
}
.mark {
    width: 22px;
    height: 22px;
    margin-top: 2px;
    flex: none;
    border-radius: 50%;
    border: 1.5px solid #cbbba6;
    display: grid;
    place-items: center;
}
.dish:has(input:checked) {
    background: #fff4ee;
    border-color: #e7b39f;
}
.dish:has(input:checked) .mark {
    background: var(--chili);
    border-color: var(--chili);
}
.dish:has(input:checked) .mark::after {
    content: "";
    width: 5px;
    height: 9px;
    border: solid #fffaf3;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg) translate(-1px, -1px);
}
.dish:focus-within { outline: 2px solid var(--chili); outline-offset: 3px; }
.dish-name {
    display: block;
    font-family: var(--serif);
    font-size: 1.16rem;
    font-weight: 700;
    line-height: 1.35;
}
.dish-note { display: block; margin-top: 2px; color: var(--muted); font-size: 0.92rem; }
.meta { display: block; margin-top: 4px; font-size: 0.82rem; color: var(--muted); }
.meta.fresh { color: var(--sage); font-weight: 600; }
.meta.today { color: var(--chili-deep); font-weight: 600; }
.dock {
    position: sticky;
    bottom: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 16px;
    padding: 10px 10px 10px 18px;
    background: rgba(255, 250, 243, 0.92);
    border: 1px solid var(--line);
    border-radius: 999px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(10px);
}
.dock-note { margin: 0; color: var(--muted); font-size: 0.92rem; }
.btn {
    appearance: none;
    border: 0;
    border-radius: 999px;
    padding: 0.72rem 1.15rem;
    background: var(--chili);
    color: #fffaf3;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(198, 83, 42, 0.22);
}
.btn:hover { background: #b24622; }
.btn.ghost, .btn.danger {
    background: transparent;
    color: var(--ink);
    box-shadow: none;
    border: 1px solid var(--line);
}
.btn.danger { color: var(--chili-deep); }
.btn.ghost:hover, .btn.danger:hover { background: #f6efe6; }
.btn.block { width: 100%; }
.panel {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 18px;
    box-shadow: var(--shadow);
}
.composer, .recipe-form { display: grid; gap: 10px; }
.recipe-form { grid-template-columns: 1fr 1fr; }
.recipe-form input:not([type="hidden"]) { grid-column: 1 / -1; }
.field { display: grid; gap: 6px; }
.field span { font-size: 0.8rem; color: var(--muted); font-weight: 600; }
input[type="text"], input[type="password"], input:not([type]) {
    width: 100%;
    padding: 0.75rem 0.85rem;
    border-radius: 12px;
    border: 1px solid transparent;
    background: #f6f0e6;
}
input:focus {
    outline: none;
    background: #fff;
    border-color: #e7c3b4;
    box-shadow: 0 0 0 3px rgba(198, 83, 42, 0.12);
}
.recipes { list-style: none; margin: 18px 0 0; padding: 0; display: grid; gap: 10px; }
.recipe {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 12px;
}
.section-label {
    margin: 22px 0 0;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--muted);
}
.empty {
    padding: 28px 8px;
    color: var(--muted);
}
.empty a { font-weight: 600; }
.history { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.history-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas:
        "date action"
        "main action";
    gap: 2px 12px;
    align-items: center;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 12px 12px 12px 16px;
}
.history-main { display: grid; gap: 2px; min-width: 0; grid-area: main; }
.history-date { color: var(--muted); font-size: 0.86rem; grid-area: date; }
.history-row .btn { grid-area: action; }
.history-name {
    font-family: var(--serif);
    font-weight: 700;
    font-size: 1.08rem;
    line-height: 1.35;
}
.history-gone { color: var(--muted); font-size: 0.8rem; }
.gate-card {
    position: relative;
    width: min(420px, 100%);
    overflow: hidden;
    padding: 36px 28px 28px;
    background: rgba(255, 250, 243, 0.94);
    border: 1px solid var(--line);
    border-radius: 28px;
    box-shadow: var(--shadow);
}
.watermark {
    position: absolute;
    top: -34px;
    right: -6px;
    margin: 0;
    font-family: var(--serif);
    font-size: 148px;
    line-height: 1;
    color: rgba(198, 83, 42, 0.09);
    pointer-events: none;
    user-select: none;
}
.gate-card h1, .gate-card .lede, .gate-card form, .gate-card .notice { position: relative; }
.stack { display: grid; gap: 14px; margin-top: 8px; }
.miss {
    min-height: 50dvh;
    display: grid;
    align-content: center;
}
@media (min-width: 720px) {
    .history-row {
        grid-template-columns: 9.5rem minmax(0, 1fr) auto;
        grid-template-areas: "date main action";
    }
    .history-date { color: var(--ink); font-size: 0.95rem; }
    .composer { grid-template-columns: 1fr 1.4fr auto; align-items: end; }
    .recipe-form {
        grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.3fr) auto auto;
        align-items: center;
    }
    .recipe-form input:not([type="hidden"]) { grid-column: auto; }
}
@media (prefers-reduced-motion: reduce) {
    .dish { transition: none; }
}
</style>
</head>
<body class="__KIND__">
__BODY__
</body>
</html>
"""


def page(title, body, kind="app"):
    rendered = (
        PAGE.replace("__TITLE__", escape(title))
        .replace("__KIND__", kind)
        .replace("__BODY__", body)
    )
    return Response(rendered, headers={"Content-Type": "text/html; charset=utf-8"})


def redirect(location, set_cookie=""):
    headers = {"Location": location}
    if set_cookie:
        headers["Set-Cookie"] = set_cookie
    return Response("", status=303, headers=headers)


def session_token(password):
    return hmac.new(password.encode(), b"daily-menu", hashlib.sha256).hexdigest()


def session_cookie(token, max_age, request):
    secure = "; Secure" if urlparse(request.url).scheme == "https" else ""
    return (
        f"session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age={max_age}{secure}"
    )


def read_session(request):
    raw = request.headers.get("cookie") or ""
    jar = SimpleCookie()
    try:
        jar.load(raw)
    except Exception:
        return ""
    morsel = jar.get("session")
    return morsel.value if morsel else ""


def topbar(current):
    links = [
        ("/", "今天"),
        ("/recipes", "菜谱"),
        ("/history", "历史"),
    ]
    parts = []
    for href, label in links:
        active = " is-active" if href == current else ""
        parts.append(f'<a class="nav-link{active}" href="{href}">{label}</a>')
    parts.append('<a class="nav-link quiet" href="/logout">退出</a>')
    return f"""
    <header class="topbar">
      <a class="brand" href="/"><span class="brand-mark">食</span><span>每日菜单</span></a>
      <nav>{"".join(parts)}</nav>
    </header>
    """


def format_day(value):
    parts = str(value).split("-")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        year, month, day = (int(part) for part in parts)
        return f"{year}年{month}月{day}日"
    return escape(str(value))


def format_used(value, today):
    if not value:
        return "还没吃过", "fresh"
    if value == today:
        return "今天吃过", "today"
    parts = str(value).split("-")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        year, month, day = (int(part) for part in parts)
        return f"上次 {year}年{month}月{day}日", "used"
    return f"上次 {escape(str(value))}", "used"


class Default(WorkerEntrypoint):
    def configured_password(self):
        try:
            value = self.env.MENU_PASSWORD
        except Exception:
            return ""
        if not value:
            return ""
        return str(value)

    def authenticated(self, request):
        secret = self.configured_password()
        if not secret:
            return False
        token = read_session(request)
        expected = session_token(secret)
        if len(token) != len(expected):
            return False
        return hmac.compare_digest(token, expected)

    async def fetch(self, request):
        path = urlparse(request.url).path
        if path == "/login":
            return await self.login(request)
        if path == "/logout":
            return redirect("/login", session_cookie("deleted", 0, request))
        if not self.authenticated(request):
            return redirect("/login")
        if path == "/":
            return await self.menu(request)
        if path == "/recipes":
            return await self.recipes(request)
        if path == "/history":
            return await self.history(request)
        body = """
        <main class="wrap miss">
          <p class="eyebrow">404</p>
          <h1>这页不在菜单上</h1>
          <p class="lede"><a href="/">回到今天</a></p>
        </main>
        """
        return page("找不到页面", body, kind="app")

    async def login(self, request):
        if self.authenticated(request):
            return redirect("/")
        message = ""
        secret = self.configured_password()
        if request.method == "POST":
            form = await request.form_data()
            given = form.get("password") or ""
            if not secret:
                message = "服务器还没有设置口令"
            elif hmac.compare_digest(given, secret):
                year = 60 * 60 * 24 * 400
                return redirect("/", session_cookie(session_token(secret), year, request))
            else:
                message = "口令不对"
        notice = f'<p class="notice" role="alert">{escape(message)}</p>' if message else ""
        body = f"""
        <main class="gate-card">
          <p class="watermark" aria-hidden="true">食</p>
          <p class="eyebrow">家庭厨房</p>
          <h1>每日菜单</h1>
          <p class="lede">记下今天吃了什么。最久没吃的排在前面。</p>
          {notice}
          <form class="stack" method="post" action="/login">
            <label class="field">
              <span>口令</span>
              <input type="password" name="password" required autocomplete="current-password" placeholder="家庭口令">
            </label>
            <button class="btn block" type="submit">进入</button>
          </form>
        </main>
        """
        return page("登录 · 每日菜单", body, kind="gate")

    async def menu(self, request):
        if request.method == "POST":
            form = await request.form_data()
            selected = form.get_all("name")
            today = date.today().isoformat()
            statements = []
            for name in selected:
                statements.append(
                    self.env.DB.prepare(
                        "UPDATE recipe SET last_used = ? WHERE name = ?"
                    ).bind(today, name)
                )
                statements.append(
                    self.env.DB.prepare(
                        "INSERT INTO usage_history (recipe_id, name, used_at) "
                        "SELECT id, name, ? FROM recipe WHERE name = ? "
                        "AND NOT EXISTS ("
                        "SELECT 1 FROM usage_history "
                        "WHERE recipe_id = recipe.id AND used_at = ?"
                        ")"
                    ).bind(today, name, today)
                )
            if statements:
                await self.env.DB.batch(statements)

        today = date.today().isoformat()
        loaded = await self.env.DB.prepare(
            "SELECT name, note, last_used FROM recipe "
            "ORDER BY last_used IS NOT NULL, last_used"
        ).all()
        rows = []
        for dish in loaded.results:
            name = escape(dish["name"])
            note = escape(dish["note"] or "")
            when, tone = format_used(dish["last_used"], today)
            note_html = f'<span class="dish-note">{note}</span>' if note else ""
            rows.append(
                "<li>"
                '<label class="dish">'
                f'<input type="checkbox" name="name" value="{name}">'
                '<span class="mark" aria-hidden="true"></span>'
                '<span class="dish-body">'
                f'<span class="dish-name">{name}</span>'
                f"{note_html}"
                f'<span class="meta {tone}">{when}</span>'
                "</span></label></li>"
            )
        count = len(rows)
        if rows:
            menu_html = f"""
            <form method="post" id="menu-form">
              <ul class="dishes">
                {"".join(rows)}
              </ul>
              <div class="dock">
                <p class="dock-note" id="dock-note">勾选今天要吃的</p>
                <button class="btn" type="submit" id="use-btn">记下来</button>
              </div>
            </form>
            <script>
              const form = document.getElementById("menu-form");
              const note = document.getElementById("dock-note");
              const button = document.getElementById("use-btn");
              const sync = () => {{
                const picked = form.querySelectorAll("input:checked").length;
                note.textContent = picked ? "已选 " + picked + " 道" : "勾选今天要吃的";
                button.textContent = picked ? "记下来 · " + picked : "记下来";
              }};
              form.addEventListener("change", sync);
            </script>
            """
        else:
            menu_html = """
            <div class="panel empty">
              <p>菜谱还是空的。</p>
              <a href="/recipes">先去添几道菜</a>
            </div>
            """
        summary = f"共 {count} 道。最久没吃的排在前面。" if count else "先把常做的菜写进菜谱。"
        body = f"""
        <div class="wrap">
          {topbar("/")}
          <p class="eyebrow">今天</p>
          <h1>吃什么</h1>
          <p class="lede">{summary}</p>
          {menu_html}
        </div>
        """
        return page("今天 · 每日菜单", body)

    async def recipes(self, request):
        message = ""
        if request.method == "POST":
            form = await request.form_data()
            action = form.get("action")
            name = (form.get("name") or "").strip()
            note = (form.get("note") or "").strip()
            original = (form.get("original") or "").strip()
            if action == "delete":
                await self.env.DB.batch(
                    [
                        self.env.DB.prepare(
                            "UPDATE usage_history SET name = ? "
                            "WHERE recipe_id = (SELECT id FROM recipe WHERE name = ?)"
                        ).bind(original, original),
                        self.env.DB.prepare(
                            "DELETE FROM recipe WHERE name = ?"
                        ).bind(original),
                    ]
                )
                return Response("", status=303, headers={"Location": "/recipes"})
            if not name:
                message = "请填写菜名"
            elif action == "update":
                try:
                    await self.env.DB.prepare(
                        "UPDATE recipe SET name = ?, note = ? WHERE name = ?"
                    ).bind(name, note, original).run()
                except Exception as error:
                    if "UNIQUE" not in str(error):
                        raise
                    message = "这道菜已经有了"
                else:
                    await self.reattach_history(name)
                    return Response("", status=303, headers={"Location": "/recipes"})
            else:
                try:
                    await self.env.DB.prepare(
                        "INSERT INTO recipe (name, note) VALUES (?, ?)"
                    ).bind(name, note).run()
                except Exception as error:
                    if "UNIQUE" not in str(error):
                        raise
                    message = "这道菜已经有了"
                else:
                    await self.reattach_history(name)
                    return Response("", status=303, headers={"Location": "/recipes"})

        loaded = await self.env.DB.prepare(
            "SELECT name, note FROM recipe ORDER BY name"
        ).all()
        rows = []
        for recipe in loaded.results:
            current = escape(recipe["name"])
            note = escape(recipe["note"] or "")
            rows.append(
                '<li class="recipe">'
                '<form method="post" action="/recipes" class="recipe-form">'
                f'<input type="hidden" name="original" value="{current}">'
                f'<input name="name" value="{current}" required aria-label="菜名">'
                f'<input name="note" value="{note}" placeholder="备注" aria-label="备注">'
                '<button class="btn ghost" type="submit" name="action" value="update">保存</button>'
                '<button class="btn danger" type="submit" name="action" value="delete" '
                "onclick=\"return confirm('删除这道菜？使用记录会留在历史里。')\">删除</button>"
                "</form></li>"
            )
        notice = f'<p class="notice" role="alert">{escape(message)}</p>' if message else ""
        catalog = (
            f'<p class="section-label">已有 {len(rows)} 道</p><ul class="recipes">{"".join(rows)}</ul>'
            if rows
            else '<p class="empty">还没有菜。上面写上第一道。</p>'
        )
        body = f"""
        <div class="wrap">
          {topbar("/recipes")}
          <p class="eyebrow">菜谱</p>
          <h1>家里的菜</h1>
          <p class="lede">名字不要重复，备注写给自己看。</p>
          {notice}
          <form class="panel composer" method="post" action="/recipes">
            <label class="field">
              <span>菜名</span>
              <input name="name" required placeholder="番茄炒蛋">
            </label>
            <label class="field">
              <span>备注</span>
              <input name="note" placeholder="可空">
            </label>
            <button class="btn" type="submit">添上</button>
          </form>
          {catalog}
        </div>
        """
        return page("菜谱 · 每日菜单", body)

    async def reattach_history(self, name):
        found = await self.env.DB.prepare(
            "SELECT id FROM recipe WHERE name = ?"
        ).bind(name).all()
        if not found.results:
            return
        recipe_id = found.results[0]["id"]
        await self.env.DB.batch(
            [
                self.env.DB.prepare(
                    "DELETE FROM usage_history WHERE recipe_id IS NULL AND name = ? "
                    "AND used_at IN ("
                    "SELECT used_at FROM usage_history WHERE recipe_id = ?"
                    ")"
                ).bind(name, recipe_id),
                self.env.DB.prepare(
                    "UPDATE usage_history SET recipe_id = ? "
                    "WHERE recipe_id IS NULL AND name = ?"
                ).bind(recipe_id, name),
                self.env.DB.prepare(
                    "UPDATE recipe SET last_used = ("
                    "SELECT MAX(used_at) FROM usage_history WHERE recipe_id = ?"
                    ") WHERE id = ?"
                ).bind(recipe_id, recipe_id),
            ]
        )

    async def history(self, request):
        if request.method == "POST":
            form = await request.form_data()
            raw_id = str(form.get("id") or "")
            if raw_id.isdigit():
                history_id = int(raw_id)
                found = await self.env.DB.prepare(
                    "SELECT recipe_id FROM usage_history WHERE id = ?"
                ).bind(history_id).all()
                if found.results:
                    recipe_id = found.results[0]["recipe_id"]
                    statements = [
                        self.env.DB.prepare(
                            "DELETE FROM usage_history WHERE id = ?"
                        ).bind(history_id)
                    ]
                    if recipe_id is not None:
                        statements.append(
                            self.env.DB.prepare(
                                "UPDATE recipe SET last_used = ("
                                "SELECT MAX(used_at) FROM usage_history WHERE recipe_id = ?"
                                ") WHERE id = ?"
                            ).bind(recipe_id, recipe_id)
                        )
                    await self.env.DB.batch(statements)
            return Response("", status=303, headers={"Location": "/history"})

        loaded = await self.env.DB.prepare(
            "SELECT usage_history.id, usage_history.used_at, usage_history.recipe_id, "
            "COALESCE(recipe.name, usage_history.name) AS name "
            "FROM usage_history LEFT JOIN recipe ON recipe.id = usage_history.recipe_id "
            "ORDER BY usage_history.used_at DESC, usage_history.id DESC"
        ).all()
        rows = []
        for item in loaded.results:
            gone = ""
            if item["recipe_id"] is None:
                gone = '<span class="history-gone">已不在菜谱里</span>'
            rows.append(
                "<li>"
                '<form method="post" action="/history" class="history-row">'
                f'<input type="hidden" name="id" value="{int(item["id"])}">'
                f'<span class="history-date">{format_day(item["used_at"])}</span>'
                '<span class="history-main">'
                f'<span class="history-name">{escape(item["name"])}</span>'
                f"{gone}"
                "</span>"
                '<button class="btn danger" type="submit" '
                "onclick=\"return confirm('删除这条记录？最近使用会按剩下的记录重算。')\">删除</button>"
                "</form></li>"
            )
        if rows:
            catalog = f'<ul class="history">{"".join(rows)}</ul>'
        else:
            catalog = '<p class="empty">还没有记录。在今天勾上菜，再记下来。</p>'
        body = f"""
        <div class="wrap">
          {topbar("/history")}
          <p class="eyebrow">历史</p>
          <h1>吃过的</h1>
          <p class="lede">新的在上面。删掉一条，这道菜的最近使用会按剩下的记录重算。</p>
          {catalog}
        </div>
        """
        return page("历史 · 每日菜单", body)
