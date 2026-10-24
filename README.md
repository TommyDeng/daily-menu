# 每日菜单

家庭共用的菜谱与「今天吃什么」小工具。用口令登录后，按最久没吃排序勾选今日菜品，并保留食用历史；忘了记的日子可以事后补上。

线上域名：`menu.tommydeng.org`（见 `wrangler.jsonc`）。

## 功能

- **今天**：菜谱按 `last_used` 排序（最久没吃的在前）；勾选后记为今天吃过，并写入历史
- **菜谱**：增删改菜名与备注；删除菜品时历史记录保留菜名
- **历史**：按日查看、补记漏记、改日期或删除；删除菜品后的记录会标「已不在菜谱里」
- **登录**：共享家庭口令（`MENU_PASSWORD`），Cookie 会话

## 界面

**今天** —— 最久没吃的排在前面，勾选后记为今天吃过。

<img src="https://img.tommydeng.org/2026/10/170458-menu.png" alt="今天页面" width="720">

**菜谱** —— 增删改菜名与备注。

<img src="https://img.tommydeng.org/2026/10/170500-recipes.png" alt="菜谱页面" width="720">

**历史** —— 按日查看、补记漏记、改日期或删除。

<img src="https://img.tommydeng.org/2026/10/170502-history.png" alt="历史页面" width="720">

## 技术栈

| 层 | 选型 |
| --- | --- |
| 运行时 | Cloudflare Workers（Python Workers） |
| 入口 | `src/entry.py`（HTML 表单 + 服务端渲染） |
| 数据 | Cloudflare D1（`DB` binding，库名 `daily-menu`） |
| 工具 | Node（`wrangler`）+ `uv` / `pywrangler` |

## 本地运行

需要：Node.js、[`uv`](https://docs.astral.sh/uv/)、已登录的 Cloudflare 账号（本地 D1 可按 Wrangler 惯例使用）。

```bash
npm install
echo 'MENU_PASSWORD=你的口令' > .dev.vars   # 已被 .gitignore，勿提交
npm run dev
```

`npm run dev` 即 `uv run pywrangler dev`。浏览器打开本地地址后用口令登录。

### 数据库迁移

迁移文件在 `migrations/`：

1. `0001_init.sql` — `recipe`、`usage_history`
2. `0002_history_keeps_name.sql` — 历史保留菜名，删除菜品后记录仍可查

本地 / 远程分别应用（按你本机 Wrangler 习惯）：

```bash
npx wrangler d1 migrations apply daily-menu --local
npx wrangler d1 migrations apply daily-menu --remote
```

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `MENU_PASSWORD` | 家庭登录口令。未设置时无法登录。本地写在 `.dev.vars`；线上用 Worker secret |

设置线上 secret：

```bash
npx wrangler secret put MENU_PASSWORD
```

## 部署

确认 D1 已创建并绑定（`wrangler.jsonc` 中的 `database_id`）、迁移已应用到远程、secret 已设置后：

```bash
npm run deploy
```

即 `uv run pywrangler deploy`。自定义域名在 `wrangler.jsonc` 的 `routes` 中配置。

## 约定

- 业务逻辑与页面都在 `src/entry.py`；无单独前端构建
- 路由：`/` 今天、`/recipes` 菜谱、`/history` 历史、`/login` / `/logout`
- `.dev.vars`、`node_modules/`、`.venv*`、`.wrangler/` 不入库
- 同一道菜同一天只记一条历史（唯一约束）
