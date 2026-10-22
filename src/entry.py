import hashlib
import hmac
from datetime import date
from html import escape
from http.cookies import SimpleCookie
from urllib.parse import urlparse

from workers import Response, WorkerEntrypoint


def page(title, body):
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__TITLE__</title>
    <style>
        body { font-family: sans-serif; margin: 1.5rem; line-height: 1.5; }
        li { margin: 0.5rem 0; }
        label { display: block; margin: 0.5rem 0; }
        input, button { font: inherit; }
        .recipe form {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            align-items: center;
            margin: 0.25rem 0 0.75rem;
        }
    </style>
    </head>
    <body>
    <h1>__TITLE__</h1>
    __BODY__
    </body>
    </html>
    """
    rendered = html.replace("__TITLE__", escape(title)).replace("__BODY__", body)
    return Response(rendered, headers={"Content-Type": "text/html; charset=utf-8"})


def redirect(location, set_cookie=""):
    headers = {"Location": location}
    if set_cookie:
        headers["Set-Cookie"] = set_cookie
    return Response("", status=303, headers=headers)


def session_token(password):
    return hmac.new(password.encode(), b"daily-menu", hashlib.sha256).hexdigest()


def session_cookie(token, max_age):
    return (
        f"session={token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age={max_age}"
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
            return redirect("/login", session_cookie("deleted", 0))
        if not self.authenticated(request):
            return redirect("/login")
        if path == "/":
            return await self.menu(request)
        if path == "/recipes":
            return await self.recipes(request)
        return Response("找不到页面", status=404)

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
                return redirect("/", session_cookie(session_token(secret), year))
            else:
                message = "口令不对"
        notice = f"<p>{escape(message)}</p>" if message else ""
        body = f"""
        {notice}
        <form method="post" action="/login">
        <label>口令 <input type="password" name="password" required></label>
        <button type="submit">进入</button>
        </form>
        """
        return page("登录", body)

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
                        "INSERT INTO usage_history (recipe_id, used_at) "
                        "SELECT id, ? FROM recipe WHERE name = ?"
                    ).bind(today, name)
                )
            if statements:
                await self.env.DB.batch(statements)

        loaded = await self.env.DB.prepare(
            "SELECT name, last_used FROM recipe ORDER BY last_used IS NOT NULL, last_used"
        ).all()
        rows = []
        for dish in loaded.results:
            name = escape(dish["name"])
            when = "还没吃过" if dish["last_used"] is None else dish["last_used"]
            rows.append(
                f'<li><label><input type="checkbox" name="name" value="{name}"> '
                f"{name} · {escape(when)}</label></li>"
            )
        body = """
        <p><a href="/recipes">维护菜谱</a> · <a href="/logout">退出</a></p>
        <form method="post">
        <ul>
            __ROWS__
        </ul>
        <button type="submit">使用</button>
        </form>
        """.replace("__ROWS__", "\n".join(rows))
        return page("每日菜单", body)

    async def recipes(self, request):
        message = ""
        if request.method == "POST":
            form = await request.form_data()
            action = form.get("action")
            name = (form.get("name") or "").strip()
            note = (form.get("note") or "").strip()
            original = (form.get("original") or "").strip()
            if action == "delete":
                await self.env.DB.prepare("DELETE FROM recipe WHERE name = ?").bind(
                    original
                ).run()
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
                    return Response("", status=303, headers={"Location": "/recipes"})

        loaded = await self.env.DB.prepare(
            "SELECT name, note FROM recipe ORDER BY name"
        ).all()
        rows = []
        for recipe in loaded.results:
            current = escape(recipe["name"])
            note = escape(recipe["note"] or "")
            rows.append(
                "<li class=\"recipe\">"
                '<form method="post" action="/recipes">'
                f'<input type="hidden" name="original" value="{current}">'
                f'<input name="name" value="{current}" required>'
                f'<input name="note" value="{note}" placeholder="备注">'
                '<button type="submit" name="action" value="update">保存</button>'
                '<button type="submit" name="action" value="delete">删除</button>'
                "</form></li>"
            )
        notice = f"<p>{escape(message)}</p>" if message else ""
        body = f"""
        <p><a href="/">返回菜单</a> · <a href="/logout">退出</a></p>
        {notice}
        <form method="post" action="/recipes">
        <label>菜名 <input name="name" required></label>
        <label>备注 <input name="note"></label>
        <button type="submit">添加</button>
        </form>
        <ul>
            {"".join(rows)}
        </ul>
        """
        return page("菜谱", body)
