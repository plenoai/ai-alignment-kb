# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "cognee>=0.5.3",
#   "langfuse>=2.32.0,<3",
#   "python-dotenv>=1.0",
# ]
# ///
"""wiki ページ構造と cognee ナレッジグラフを統合して可視化する。

使い方:
  uv run visualize.py           # 統合グラフ（cognee が空なら wiki のみ）
  uv run visualize.py --wiki    # wiki リンクのみ

出力: graph.html
"""

import argparse
import asyncio
import json
import os
import re
import sys
import webbrowser
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import cognee  # noqa: E402
from cognee.infrastructure.databases.graph import get_graph_engine  # noqa: E402

WIKI_DIR = Path(__file__).parent / "wiki"
DATA_DIR = Path(__file__).parent / ".data"
OUTPUT = Path(__file__).parent / "docs" / "index.html"
LINK_RE = re.compile(r"\[([^\]]+)\]\(\.?/?([^)#]+)\.md\)")

# wiki ページ種別タグ → 色（大ノード）
PAGE_TYPE_COLOR: dict[str, str] = {
    "tag-pattern":  "#4f8ef7",
    "tag-concept":  "#f7a94f",
    "tag-case":     "#4fc98e",
}
# wiki サブドメインタグ → アクセント色（ボーダー）
SUBDOMAIN_COLOR: dict[str, str] = {
    "tag-scalable-oversight": "#c084fc",
    "tag-rlhf":               "#f472b6",
    "tag-constitutional-ai":  "#fb923c",
    "tag-interpretability":   "#34d399",
}
DEFAULT_PAGE_COLOR = "#94a3b8"
ENTITY_COLOR       = "#1e3a5f"   # 濃紺: cognee エンティティ（小ノード）
ANCHOR_EDGE_COLOR  = "#1e293b"   # エンティティ→ページの薄いエッジ
WIKI_EDGE_COLOR    = "#475569"   # wiki ページ間リンク
COGNEE_EDGE_COLOR  = "#0f3460"   # cognee エンティティ間リレーション


# ── wiki メタ収集 ─────────────────────────────────────────────────────────────

def collect_wiki_meta() -> dict[str, dict]:
    pages = {p.stem: p for p in WIKI_DIR.glob("*.md")}
    meta: dict[str, dict] = {}
    for stem, path in pages.items():
        text = path.read_text(encoding="utf-8")
        title_m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else stem
        tags: set[str] = set()
        links: set[str] = set()
        for _, target in LINK_RE.findall(text):
            target = target.rstrip("/")
            if target.startswith("tag-"):
                tags.add(target)
            elif target in pages and target != stem:
                links.add(target)
        meta[stem] = {"title": title, "tags": tags, "links": links, "text_head": text[:100]}
    return meta


# ── cognee グラフ収集 ─────────────────────────────────────────────────────────

async def collect_cognee(wiki_meta: dict[str, dict]) -> tuple[list[dict], list[dict], dict[str, str]]:
    """
    Returns:
        entity_nodes  — Entity ノードのリスト
        entity_edges  — Entity 間エッジのリスト
        entity_to_wiki — entity_id → wiki page stem
    """
    cognee.config.data_root_directory(str(DATA_DIR))
    cognee.config.set_llm_api_key(os.environ["OPENAI_API_KEY"])
    cognee.config.set_llm_provider("openai")
    cognee.config.set_llm_model("gpt-4.1")

    engine = await get_graph_engine()

    # TextDocument の name → raw_data_location
    doc_rows = await engine.query(
        'MATCH (d:Node) WHERE d.type = "TextDocument" RETURN d.name, d.properties'
    )
    doc_to_file: dict[str, Path] = {}
    for row in doc_rows:
        props = json.loads(row[1])
        loc = props.get("raw_data_location", "").replace("file://", "")
        if loc:
            doc_to_file[row[0]] = Path(loc)

    # .data/ ファイル先頭 50 文字で wiki ページを特定
    file_to_wiki: dict[str, str] = {}
    for doc_name, file_path in doc_to_file.items():
        if not file_path.exists():
            continue
        head = file_path.read_text(encoding="utf-8")[:50]
        for stem, m in wiki_meta.items():
            if m["text_head"][:50] == head:
                file_to_wiki[doc_name] = stem
                break

    # DocumentChunk id → doc_name
    chunk_rows = await engine.query(
        'MATCH (c:Node)-[r]->(d:Node) WHERE c.type = "DocumentChunk" AND d.type = "TextDocument" RETURN c.id, d.name'
    )
    chunk_to_doc: dict[str, str] = {r[0]: r[1] for r in chunk_rows}

    # Entity id → wiki page stem
    entity_chunk_rows = await engine.query(
        'MATCH (c:Node)-[r]->(e:Node) WHERE c.type = "DocumentChunk" AND e.type = "Entity" RETURN e.id, c.id'
    )
    entity_to_wiki: dict[str, str] = {}
    for entity_id, chunk_id in entity_chunk_rows:
        doc_name = chunk_to_doc.get(chunk_id)
        wiki = file_to_wiki.get(doc_name) if doc_name else None
        if wiki:
            entity_to_wiki[entity_id] = wiki

    # Entity ノード
    entity_rows = await engine.query(
        'MATCH (e:Node) WHERE e.type = "Entity" RETURN e.id, e.name, e.properties'
    )
    entity_nodes: list[dict] = []
    for row in entity_rows:
        eid, name, props_str = row
        props = json.loads(props_str)
        entity_nodes.append({
            "id": str(eid),
            "label": name[:40] if name else str(eid)[:20],
            "color": ENTITY_COLOR,
            "size": 6,
            "kind": "entity",
            "wiki": entity_to_wiki.get(str(eid), ""),
            "description": props.get("description", "")[:200],
        })

    # Entity 間エッジ
    edge_rows = await engine.query(
        'MATCH (a:Node)-[r]->(b:Node) WHERE a.type = "Entity" AND b.type = "Entity" RETURN a.id, b.id, r.relationship_name'
    )
    seen: set[tuple[str, str]] = set()
    entity_edges: list[dict] = []
    for src, dst, rel in edge_rows:
        key = (str(src), str(dst))
        if key not in seen:
            seen.add(key)
            entity_edges.append({"from": str(src), "to": str(dst), "label": rel or ""})

    return entity_nodes, entity_edges, entity_to_wiki


# ── HTML 生成 ─────────────────────────────────────────────────────────────────

HTML = r"""\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Alignment KB — Unified Knowledge Graph</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<script src="https://unpkg.com/marked@12.0.0/marked.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
html, body { height:100%; background:#060e1a; color:#e2e8f0; font-family:system-ui,sans-serif; overflow:hidden; }

/* ── レイアウト ── */
#app { display:flex; height:100vh; }
#graph-wrap { flex:1; position:relative; min-width:0; }
#graph { width:100%; height:100%; }

/* ── 右ペイン ── */
#reader {
  width:0; overflow:hidden; transition:width .25s ease;
  background:#0b1627; border-left:1px solid #1e293b;
  display:flex; flex-direction:column;
}
#reader.open { width:420px; }
#reader-header {
  display:flex; align-items:center; justify-content:space-between;
  padding:12px 16px; border-bottom:1px solid #1e293b; flex-shrink:0;
  gap:8px;
}
#reader-title { font-size:13px; font-weight:600; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
#reader-close {
  flex-shrink:0; background:none; border:none; color:#475569; cursor:pointer;
  font-size:18px; line-height:1; padding:2px 4px; border-radius:4px;
}
#reader-close:hover { color:#e2e8f0; background:#1e293b; }
#reader-body {
  flex:1; overflow-y:auto; padding:20px 20px 40px;
  scrollbar-width:thin; scrollbar-color:#1e293b transparent;
}

/* ── Markdown スタイル ── */
#reader-body h1 { font-size:1.3em; color:#e2e8f0; margin:0 0 12px; line-height:1.3; }
#reader-body h2 { font-size:1.05em; color:#cbd5e1; margin:22px 0 8px; border-bottom:1px solid #1e293b; padding-bottom:4px; }
#reader-body h3 { font-size:.95em; color:#94a3b8; margin:16px 0 6px; }
#reader-body p  { font-size:.88em; color:#94a3b8; line-height:1.75; margin-bottom:10px; }
#reader-body ul, #reader-body ol { padding-left:1.4em; margin-bottom:10px; }
#reader-body li { font-size:.88em; color:#94a3b8; line-height:1.7; }
#reader-body a  { color:#4f8ef7; text-decoration:none; }
#reader-body a:hover { text-decoration:underline; }
#reader-body code { font-family:ui-monospace,monospace; font-size:.82em; background:#0f172a; color:#7dd3fc; padding:1px 5px; border-radius:3px; }
#reader-body pre { background:#0f172a; border:1px solid #1e293b; border-radius:6px; padding:12px; overflow-x:auto; margin-bottom:12px; }
#reader-body pre code { background:none; padding:0; font-size:.82em; color:#7dd3fc; }
#reader-body blockquote { border-left:3px solid #334155; margin:0 0 10px; padding:4px 12px; color:#64748b; font-size:.88em; }
#reader-body table { width:100%; border-collapse:collapse; margin-bottom:12px; font-size:.83em; }
#reader-body th { background:#0f172a; color:#cbd5e1; padding:6px 8px; text-align:left; border:1px solid #1e293b; }
#reader-body td { color:#94a3b8; padding:5px 8px; border:1px solid #1e293b; }
#reader-body strong { color:#cbd5e1; }
#reader-body hr { border:none; border-top:1px solid #1e293b; margin:14px 0; }

/* ── 左パネル ── */
#panel {
  position:absolute; top:14px; left:14px; z-index:10;
  background:rgba(6,14,26,.92); border:1px solid #1e293b;
  border-radius:10px; padding:14px 16px; font-size:12px;
  backdrop-filter:blur(8px); width:220px;
  transition:transform .2s ease;
}
#panel h2 { font-size:11px; color:#475569; letter-spacing:.08em; text-transform:uppercase; margin-bottom:10px; }
.legend-row { display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.dot    { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.dot-sm { width:7px;  height:7px;  border-radius:50%; flex-shrink:0; }
.divider { border:none; border-top:1px solid #1e293b; margin:10px 0; }
.toggle-row { display:flex; align-items:center; gap:8px; margin-bottom:6px; cursor:pointer; user-select:none; }
.toggle-row input { accent-color:#4f8ef7; cursor:pointer; }
#detail { margin-top:10px; color:#94a3b8; line-height:1.6; font-size:11px; min-height:36px; }
#detail strong { color:#e2e8f0; }
#stats  { color:#334155; font-size:10px; margin-top:8px; }

/* ── 検索 ── */
#search-wrap { position:relative; margin-bottom:10px; }
#search-input {
  width:100%; padding:6px 8px 6px 28px; border:1px solid #1e293b; border-radius:6px;
  background:#0b1627; color:#e2e8f0; font-size:12px; outline:none;
}
#search-input:focus { border-color:#4f8ef7; }
#search-icon { position:absolute; left:8px; top:50%; transform:translateY(-50%); color:#475569; font-size:12px; pointer-events:none; }
#search-results {
  position:absolute; top:100%; left:0; right:0; margin-top:4px;
  background:rgba(11,22,39,.98); border:1px solid #1e293b; border-radius:6px;
  max-height:260px; overflow-y:auto; display:none; z-index:50;
  scrollbar-width:thin; scrollbar-color:#1e293b transparent;
}
#search-results.open { display:block; }
.sr-item {
  padding:6px 10px; cursor:pointer; font-size:11px; color:#94a3b8;
  border-bottom:1px solid #0f172a;
}
.sr-item:last-child { border-bottom:none; }
.sr-item:hover, .sr-item.active { background:#1e293b; color:#e2e8f0; }
.sr-item .sr-title { color:#e2e8f0; font-weight:600; }
.sr-item .sr-snippet { color:#64748b; font-size:10px; margin-top:2px; display:block; }
.sr-item mark { background:#4f8ef720; color:#7dd3fc; border-radius:2px; padding:0 1px; }

/* ── ハンバーガー（スマホ用パネル開閉）── */
#menu-btn {
  display:none; position:absolute; top:12px; left:12px; z-index:20;
  background:rgba(6,14,26,.9); border:1px solid #1e293b; border-radius:8px;
  color:#e2e8f0; font-size:18px; width:38px; height:38px;
  cursor:pointer; align-items:center; justify-content:center;
}

/* ── ツールチップ ── */
#tooltip {
  display:none; position:fixed; background:rgba(6,14,26,.95);
  border:1px solid #1e293b; border-radius:5px; padding:5px 9px;
  font-size:11px; pointer-events:none; max-width:220px; z-index:30;
  word-break:break-all; line-height:1.5;
}

/* ── スマホ対応 ── */
@media (max-width: 640px) {
  #reader.open { width:100vw; position:fixed; top:0; left:0; right:0; bottom:0; z-index:40; }
  #panel { width:calc(100vw - 28px); transform:translateY(-120%); }
  #panel.sp-open { transform:translateY(0); }
  #menu-btn { display:flex; }
  #reader-body h1 { font-size:1.1em; }
}
</style>
</head>
<body>
<div id="app">
  <div id="graph-wrap">
    <div id="graph"></div>
    <button id="menu-btn" onclick="togglePanel()" title="メニュー">☰</button>
    <div id="panel">
      <h2>AI Alignment KB</h2>
      <div id="search-wrap">
        <svg id="search-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="10" cy="10" r="7"/><line x1="15" y1="15" x2="21" y2="21"/></svg>
        <input id="search-input" type="text" placeholder="ページを検索…" autocomplete="off" spellcheck="false">
        <div id="search-results"></div>
      </div>
      <div class="legend-row"><div class="dot" style="background:#4f8ef7"></div>パターン (wiki)</div>
      <div class="legend-row"><div class="dot" style="background:#f7a94f"></div>コンセプト (wiki)</div>
      <div class="legend-row"><div class="dot" style="background:#4fc98e"></div>事例 (wiki)</div>
      <div class="legend-row"><div class="dot-sm" style="background:#1e3a5f;border:1px solid #4f8ef7"></div>エンティティ (cognee)</div>
      <hr class="divider">
      <label class="toggle-row"><input type="checkbox" id="tog-wiki-links" checked> wiki ページ間リンク</label>
      <label class="toggle-row"><input type="checkbox" id="tog-entities" checked> cognee エンティティ</label>
      <label class="toggle-row"><input type="checkbox" id="tog-entity-links" checked> エンティティ間リレーション</label>
      <label class="toggle-row"><input type="checkbox" id="tog-anchors" checked> エンティティ↔ページ接続</label>
      <hr class="divider">
      <div id="detail">ページノードをタップして内容を表示</div>
      <div id="stats">STATS_TEXT</div>
    </div>
  </div>

  <!-- 右ペイン: Markdown リーダー -->
  <div id="reader">
    <div id="reader-header">
      <span id="reader-title"></span>
      <button id="reader-close" onclick="closeReader()" title="閉じる">✕</button>
    </div>
    <div id="reader-body"></div>
  </div>
</div>

<div id="tooltip"></div>

<script>
const PAGE_NODES   = PAGE_NODES_JSON;
const PAGE_EDGES   = PAGE_EDGES_JSON;
const ENT_NODES    = ENT_NODES_JSON;
const ENT_EDGES    = ENT_EDGES_JSON;
const ANCHOR_EDGES = ANCHOR_EDGES_JSON;
const MD_CONTENTS  = MD_CONTENTS_JSON;   // { stem: markdown_string }

// ── データセット ──────────────────────────────────────────────────────────────
const allNodes = new vis.DataSet([...PAGE_NODES, ...ENT_NODES]);
const allEdges = new vis.DataSet([
  ...PAGE_EDGES.map(e => ({...e, group:"wiki"})),
  ...ENT_EDGES.map(e => ({...e, group:"entity"})),
  ...ANCHOR_EDGES.map(e => ({...e, group:"anchor"})),
]);

// ── グラフ ────────────────────────────────────────────────────────────────────
const container = document.getElementById("graph");
const network = new vis.Network(container, { nodes: allNodes, edges: allEdges }, {
  nodes: {
    shape: "dot",
    font: { color: "#e2e8f0", size: 10, strokeWidth: 2, strokeColor: "#060e1a" },
    borderWidth: 1.5,
  },
  edges: {
    width: 1,
    smooth: { type: "continuous" },
    arrows: { to: { enabled: true, scaleFactor: 0.4 } },
    selectionWidth: 2,
  },
  physics: {
    solver: "forceAtlas2Based",
    forceAtlas2Based: { gravitationalConstant: -120, springLength: 160, springConstant: 0.05, damping: 0.4 },
    stabilization: { iterations: 250, updateInterval: 25 },
  },
  interaction: { hover: true, multiselect: false },
});

// ── トグル ────────────────────────────────────────────────────────────────────
function applyToggles() {
  allNodes.update(ENT_NODES.map(n => ({ id: n.id, hidden: !document.getElementById("tog-entities").checked })));
  allEdges.update(allEdges.get().map(e => {
    const showWiki   = document.getElementById("tog-wiki-links").checked;
    const showEnt    = document.getElementById("tog-entities").checked;
    const showRel    = document.getElementById("tog-entity-links").checked;
    const showAnchor = document.getElementById("tog-anchors").checked;
    return { id: e.id, hidden:
      (e.group === "wiki"   && !showWiki) ||
      (e.group === "entity" && (!showRel || !showEnt)) ||
      (e.group === "anchor" && (!showAnchor || !showEnt))
    };
  }));
}
["tog-wiki-links","tog-entities","tog-entity-links","tog-anchors"].forEach(id =>
  document.getElementById(id).addEventListener("change", applyToggles)
);

// ── Markdown リーダー ────────────────────────────────────────────────────────
function openReader(stem, title) {
  const md = MD_CONTENTS[stem];
  if (!md) return;
  document.getElementById("reader-title").textContent = title;
  // wiki 内リンクをグラフ上のノードクリックに変換
  const rendered = marked.parse(md, { breaks: false });
  document.getElementById("reader-body").innerHTML = rendered;
  // 内部リンクをインターセプト
  document.querySelectorAll("#reader-body a").forEach(a => {
    const href = a.getAttribute("href") || "";
    const m = href.match(/^(?:\.\/)?([\\w-]+)\\.md$/);
    if (m) {
      a.href = "javascript:void(0)";
      a.addEventListener("click", e => { e.preventDefault(); jumpToNode(m[1]); });
    }
  });
  document.getElementById("reader").classList.add("open");
  // グラフ幅を再計算
  setTimeout(() => { network.redraw(); network.fit(); }, 260);
}

function closeReader() {
  document.getElementById("reader").classList.remove("open");
  setTimeout(() => { network.redraw(); }, 260);
}

function jumpToNode(stem) {
  const n = allNodes.get(stem);
  if (!n) return;
  network.focus(stem, { scale: 1.2, animation: true });
  network.selectNodes([stem]);
  openReader(stem, n.label);
}

// ── 全文検索 ──────────────────────────────────────────────────────────────────
const searchInput   = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");

// 検索用インデックス: { stem, title, textLower }
const searchIndex = PAGE_NODES.map(n => ({
  stem: n.id,
  title: n.label,
  titleLower: n.label.toLowerCase(),
  textLower: (MD_CONTENTS[n.id] || "").toLowerCase(),
}));

function escapeHtml(s) { return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

function highlightTerm(text, term) {
  const idx = text.toLowerCase().indexOf(term.toLowerCase());
  if (idx === -1) return escapeHtml(text);
  return escapeHtml(text.slice(0, idx))
    + "<mark>" + escapeHtml(text.slice(idx, idx + term.length)) + "</mark>"
    + escapeHtml(text.slice(idx + term.length));
}

function extractSnippet(text, term, radius) {
  radius = radius || 40;
  const idx = text.toLowerCase().indexOf(term.toLowerCase());
  if (idx === -1) return "";
  const start = Math.max(0, idx - radius);
  const end = Math.min(text.length, idx + term.length + radius);
  let snippet = (start > 0 ? "…" : "") + text.slice(start, end).replace(/\\n/g, " ") + (end < text.length ? "…" : "");
  return highlightTerm(snippet, term);
}

let activeIdx = -1;

function doSearch() {
  const q = searchInput.value.trim();
  if (!q) { searchResults.classList.remove("open"); searchResults.innerHTML = ""; activeIdx = -1; return; }
  const ql = q.toLowerCase();
  // スコア: タイトル完全一致 > タイトル部分一致 > 本文一致
  const hits = [];
  for (const entry of searchIndex) {
    const inTitle = entry.titleLower.includes(ql);
    const inText  = entry.textLower.includes(ql);
    if (inTitle || inText) {
      hits.push({ ...entry, score: inTitle ? (entry.titleLower === ql ? 3 : 2) : 1 });
    }
  }
  hits.sort((a, b) => b.score - a.score);
  if (!hits.length) { searchResults.classList.remove("open"); searchResults.innerHTML = ""; activeIdx = -1; return; }

  searchResults.innerHTML = hits.slice(0, 20).map((h, i) => {
    const titleHtml = highlightTerm(h.title, q);
    const snippet = h.score < 2 ? extractSnippet(MD_CONTENTS[h.stem] || "", q) : "";
    return `<div class="sr-item" data-stem="${h.stem}" data-idx="${i}"><span class="sr-title">${titleHtml}</span>${snippet ? '<span class="sr-snippet">' + snippet + '</span>' : ''}</div>`;
  }).join("");
  searchResults.classList.add("open");
  activeIdx = -1;

  // マッチしたノードをグラフ上で選択
  network.selectNodes(hits.map(h => h.stem));
}

searchInput.addEventListener("input", doSearch);

// キーボードナビゲーション
searchInput.addEventListener("keydown", e => {
  const items = searchResults.querySelectorAll(".sr-item");
  if (!items.length) return;
  if (e.key === "ArrowDown") { e.preventDefault(); activeIdx = Math.min(activeIdx + 1, items.length - 1); }
  else if (e.key === "ArrowUp") { e.preventDefault(); activeIdx = Math.max(activeIdx - 1, 0); }
  else if (e.key === "Enter" && activeIdx >= 0) { e.preventDefault(); items[activeIdx].click(); return; }
  else if (e.key === "Escape") { searchResults.classList.remove("open"); searchInput.blur(); return; }
  else return;
  items.forEach((el, i) => el.classList.toggle("active", i === activeIdx));
  items[activeIdx]?.scrollIntoView({ block: "nearest" });
});

// 結果クリック
searchResults.addEventListener("click", e => {
  const item = e.target.closest(".sr-item");
  if (!item) return;
  const stem = item.dataset.stem;
  searchResults.classList.remove("open");
  jumpToNode(stem);
});

// 外側クリックで閉じる
document.addEventListener("click", e => {
  if (!e.target.closest("#search-wrap")) searchResults.classList.remove("open");
});

// ── ハンバーガー（スマホ）────────────────────────────────────────────────────
function togglePanel() {
  document.getElementById("panel").classList.toggle("sp-open");
}

// ── ツールチップ & クリック ───────────────────────────────────────────────────
const tooltip = document.getElementById("tooltip");
const detail  = document.getElementById("detail");

network.on("hoverNode", ({ node, event }) => {
  // スマホではツールチップ不要
  if (window.innerWidth <= 640) return;
  tooltip.textContent = allNodes.get(node).label;
  tooltip.style.display = "block";
  tooltip.style.left = (event.clientX + 14) + "px";
  tooltip.style.top  = (event.clientY - 10) + "px";
});
network.on("blurNode", () => { tooltip.style.display = "none"; });

network.on("click", ({ nodes: sel }) => {
  if (!sel.length) { detail.innerHTML = "ページノードをタップして内容を表示"; return; }
  const n = allNodes.get(sel[0]);
  if (n.kind === "page") {
    detail.innerHTML = `<strong>${n.label}</strong><br>`
      + `<span style="color:#475569">${n.pageType || ""} ${n.subdomain ? "/ " + n.subdomain : ""}</span>`;
    openReader(n.id, n.label);
    // 関連エンティティを強調
    const related = ENT_NODES.filter(e => e.wiki === n.id).map(e => e.id);
    if (related.length) network.selectNodes([n.id, ...related]);
  } else {
    detail.innerHTML = `<strong>${n.label}</strong><br>`
      + (n.wiki ? `<span style="color:#475569">← ${n.wiki}</span><br>` : "")
      + (n.description ? `<br><span style="color:#64748b;font-size:10px">${n.description}</span>` : "");
  }
});
</script>
</body>
</html>
"""


def build_vis_data(
    wiki_meta: dict[str, dict],
    entity_nodes: list[dict],
    entity_edges: list[dict],
    entity_to_wiki: dict[str, str],
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    # ── wiki ページノード ──
    page_nodes: list[dict] = []
    for stem, m in wiki_meta.items():
        if stem.startswith("tag-") or stem == "index":
            continue
        page_type = next((t for t in m["tags"] if t in PAGE_TYPE_COLOR), None)
        subdomain  = next((t for t in m["tags"] if t in SUBDOMAIN_COLOR), None)
        color = PAGE_TYPE_COLOR.get(page_type, DEFAULT_PAGE_COLOR)
        border = SUBDOMAIN_COLOR.get(subdomain, color)
        page_nodes.append({
            "id": stem,
            "label": m["title"],
            "color": {"background": color, "border": border, "highlight": {"background": color, "border": "#fff"}},
            "size": 20,
            "kind": "page",
            "pageType": page_type.replace("tag-", "") if page_type else "",
            "subdomain": subdomain.replace("tag-", "") if subdomain else "",
            "borderWidth": 3,
            "font": {"size": 12},
        })

    # ── wiki ページ間エッジ ──
    page_edges: list[dict] = []
    seen: set[tuple[str, str]] = set()
    page_stems = {n["id"] for n in page_nodes}
    for stem, m in wiki_meta.items():
        for target in m["links"]:
            if target not in page_stems:
                continue
            key = tuple(sorted([stem, target]))
            if key not in seen:
                seen.add(key)
                page_edges.append({
                    "from": stem, "to": target,
                    "color": {"color": WIKI_EDGE_COLOR, "highlight": "#94a3b8"},
                    "width": 2,
                    "arrows": {"to": {"enabled": False}},
                })

    # ── cognee エンティティノード ──
    ent_vis: list[dict] = []
    for e in entity_nodes:
        wiki = e.get("wiki", "")
        # ページの色を薄く反映
        page_meta = wiki_meta.get(wiki, {})
        pt = next((t for t in page_meta.get("tags", set()) if t in PAGE_TYPE_COLOR), None)
        tint = PAGE_TYPE_COLOR.get(pt, ENTITY_COLOR) if pt else ENTITY_COLOR
        ent_vis.append({
            "id": e["id"],
            "label": e["label"],
            "color": {"background": ENTITY_COLOR, "border": tint,
                      "highlight": {"background": "#1e3a5f", "border": "#fff"}},
            "size": 6,
            "borderWidth": 1,
            "kind": "entity",
            "wiki": wiki,
            "description": e.get("description", ""),
            "font": {"size": 9, "color": "#64748b"},
        })

    # ── エンティティ間エッジ ──
    ent_edge_vis: list[dict] = []
    for e in entity_edges:
        ent_edge_vis.append({
            "from": e["from"], "to": e["to"],
            "title": e.get("label", ""),
            "color": {"color": COGNEE_EDGE_COLOR, "highlight": "#334155"},
            "width": 1,
        })

    # ── アンカーエッジ（エンティティ → wiki ページ）──
    anchor_edges: list[dict] = []
    for entity_id, wiki_stem in entity_to_wiki.items():
        if wiki_stem in page_stems:
            anchor_edges.append({
                "from": entity_id, "to": wiki_stem,
                "color": {"color": ANCHOR_EDGE_COLOR, "highlight": "#334155"},
                "width": 0.5,
                "dashes": True,
                "arrows": {"to": {"enabled": False}},
            })

    return page_nodes, page_edges, ent_vis, ent_edge_vis, anchor_edges


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", action="store_true", help="wiki リンクのみ（cognee なし）")
    args = parser.parse_args()

    wiki_meta = collect_wiki_meta()
    print(f"wiki: {sum(1 for s in wiki_meta if not s.startswith('tag-') and s != 'index')} ページ")

    entity_nodes: list[dict] = []
    entity_edges: list[dict] = []
    entity_to_wiki: dict[str, str] = {}

    if not args.wiki:
        try:
            entity_nodes, entity_edges, entity_to_wiki = await collect_cognee(wiki_meta)
            print(f"cognee: エンティティ {len(entity_nodes)}  リレーション {len(entity_edges)}  紐付け {len(entity_to_wiki)}")
            if not entity_nodes:
                print("cognee グラフが空です。先に `uv run ingest.py` を実行してください。")
        except Exception as e:
            print(f"cognee スキップ: {e}", file=sys.stderr)

    page_nodes, page_edges, ent_vis, ent_edge_vis, anchor_edges = build_vis_data(
        wiki_meta, entity_nodes, entity_edges, entity_to_wiki
    )

    stats = (f"wiki {len(page_nodes)} ページ / {len(page_edges)} リンク"
             + (f" | cognee {len(ent_vis)} エンティティ / {len(ent_edge_vis)} リレーション"
                if ent_vis else ""))

    # Markdown コンテンツを埋め込む（tag- / index 以外の全ページ）
    md_contents: dict[str, str] = {
        stem: m["text_head"].replace("...", "")  # text_head は先頭100文字のみなので全文を読む
        for stem, m in wiki_meta.items()
        if not stem.startswith("tag-") and stem != "index"
    }
    # 全文を改めて読む
    pages = {p.stem: p for p in WIKI_DIR.glob("*.md")}
    md_contents = {
        stem: pages[stem].read_text(encoding="utf-8")
        for stem in md_contents
        if stem in pages
    }

    html = HTML
    html = html.replace("PAGE_NODES_JSON",  json.dumps(page_nodes,   ensure_ascii=False))
    html = html.replace("PAGE_EDGES_JSON",  json.dumps(page_edges,   ensure_ascii=False))
    html = html.replace("ENT_NODES_JSON",   json.dumps(ent_vis,      ensure_ascii=False))
    html = html.replace("ENT_EDGES_JSON",   json.dumps(ent_edge_vis, ensure_ascii=False))
    html = html.replace("ANCHOR_EDGES_JSON",json.dumps(anchor_edges, ensure_ascii=False))
    html = html.replace("MD_CONTENTS_JSON", json.dumps(md_contents,  ensure_ascii=False))
    html = html.replace("STATS_TEXT", stats)

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"生成: {OUTPUT}")
    webbrowser.open(OUTPUT.as_uri())


if __name__ == "__main__":
    asyncio.run(main())
