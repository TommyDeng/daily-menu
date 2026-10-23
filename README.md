# 每日菜单

家庭菜谱小应用：按「最久没吃」排序，勾选记下今天吃了什么；可补漏记、改日期。

线上域名见 `wrangler.jsonc` 里的自定义路由（当前为 `menu.tommydeng.org`）。

## 功能

- **登录**：共用家庭口令（`MENU_PASSWORD`），HttpOnly Cookie 会话
- **今天**（`/`）：菜谱按最近使用升序（未吃过的在前）；勾选后「记下来」写入当日记录
- **菜谱**（`/recipes`）：增删改菜名与备注；删除后历史记录保留菜名
- **历史**（`/history`）：补记漏掉的日子、改日期、删记录；`last_used` 会按剩余记录重算

同一道菜同一天只记一条。

## 技术栈

- [Cloudflare Workers](https://developers.cloudflare.com/workers/)（Python Workers，`python_workers`）
- [D1](https://developers.cloudflare.com/d1/)（绑定名 `DB`）
- 单文件应用：`src/entry.py`（服务端渲染 HTML + 少量前端脚本）
- 本地/部署：`uv` + `pywrangler`（`workers-py`），Node 侧依赖 `wrangler`

## 目录

```
src/entry.py          # Worker 入口与页面
migrations/           # D1 schema 迁移
wrangler.jsonc        # Worker / D1 / 路由配置
pyproject.toml        # Python 依赖（dev: workers-py 等）
package.json          # npm scripts → pywrangler
.dev.vars             # 本地密钥（勿提交，已在 .gitignore）
```

## 本地运行

需要：Node.js、[uv](https://docs.astral.sh/uv/)、Python ≥ 3.12。

```bash
npm install
```

在项目根创建 `.dev.vars`（已被忽略，勿提交）：

```
MENU_PASSWORD=你的家庭口令
```

应用本地 D1 迁移并启动：

```bash
npx wrangler d1 migrations apply daily-menu --local
npm run dev
```

`npm run dev` 等价于 `uv run pywrangler dev`。

## 环境变量

| 变量 | 说明 |
|------|------|
| `MENU_PASSWORD` | 登录口令。未设置时无法登录（页面提示「服务器还没有设置口令」） |

本地：写在 `.dev.vars`。  
生产：用 Worker secret，例如：

```bash
npx wrangler secret put MENU_PASSWORD
```

## 部署

1. 确认 `wrangler.jsonc` 中 D1 `database_id`、自定义域名路由正确。
2. 对远程库应用迁移：

   ```bash
   npx wrangler d1 migrations apply daily-menu --remote
   ```

3. 设置 `MENU_PASSWORD` secret（若尚未设置）。
4. 部署：

   ```bash
   npm run deploy
   ```

   （`uv run pywrangler deploy`）

Observability（日志 / traces）已在 `wrangler.jsonc` 中开启。

## 约定

- UI 与文案为中文；品牌名「每日菜单」。
- 无独立前端构建：改页面即改 `src/entry.py`。
- Schema 变更只加 `migrations/` 下新文件，用 wrangler D1 migrations 应用。
- 不要提交 `.dev.vars`、`.wrangler/`、`node_modules/`、`python_modules/`、虚拟环境目录。
