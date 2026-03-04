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

HTML = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>AI Alignment KB — Unified Knowledge Graph</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#060e1a; color:#e2e8f0; font-family:system-ui,sans-serif; overflow:hidden; }
#graph { width:100vw; height:100vh; }

/* ─── パネル ─── */
#panel {
  position:fixed; top:14px; left:14px; z-index:10;
  background:rgba(6,14,26,.9); border:1px solid #1e293b;
  border-radius:10px; padding:14px 16px; font-size:12px;
  backdrop-filter:blur(8px); width:230px;
}
#panel h2 { font-size:11px; color:#475569; letter-spacing:.08em; text-transform:uppercase; margin-bottom:10px; }

.legend-row { display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.dot-sm { width:7px; height:7px; border-radius:50%; flex-shrink:0; }

.divider { border:none; border-top:1px solid #1e293b; margin:10px 0; }

/* トグル */
.toggle-row { display:flex; align-items:center; gap:8px; margin-bottom:6px; cursor:pointer; user-select:none; }
.toggle-row input { accent-color:#4f8ef7; cursor:pointer; }

/* 詳細 */
#detail { margin-top:10px; color:#94a3b8; line-height:1.6; font-size:11px; min-height:40px; }
#detail strong { color:#e2e8f0; }

/* ステータス */
#stats { color:#334155; font-size:10px; margin-top:8px; }

/* ツールチップ */
#tooltip {
  display:none; position:fixed; background:rgba(6,14,26,.95);
  border:1px solid #1e293b; border-radius:5px; padding:5px 9px;
  font-size:11px; pointer-events:none; max-width:220px; z-index:20;
  word-break:break-all; line-height:1.5;
}
</style>
</head>
<body>
<div id="graph"></div>

<div id="panel">
  <h2>AI Alignment KB</h2>

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
  <div id="detail">ノードをクリックして詳細を表示</div>
  <div id="stats">STATS_TEXT</div>
</div>

<div id="tooltip"></div>

<script>
const PAGE_NODES  = PAGE_NODES_JSON;
const PAGE_EDGES  = PAGE_EDGES_JSON;
const ENT_NODES   = ENT_NODES_JSON;
const ENT_EDGES   = ENT_EDGES_JSON;
const ANCHOR_EDGES = ANCHOR_EDGES_JSON;  // entity → wiki page

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
  const showWikiLinks   = document.getElementById("tog-wiki-links").checked;
  const showEntities    = document.getElementById("tog-entities").checked;
  const showEntityLinks = document.getElementById("tog-entity-links").checked;
  const showAnchors     = document.getElementById("tog-anchors").checked;

  const nodeUpdates = [
    ...ENT_NODES.map(n => ({ id: n.id, hidden: !showEntities })),
  ];
  allNodes.update(nodeUpdates);

  const edgeUpdates = allEdges.get().map(e => {
    let hidden = false;
    if (e.group === "wiki")   hidden = !showWikiLinks;
    if (e.group === "entity") hidden = !showEntityLinks || !showEntities;
    if (e.group === "anchor") hidden = !showAnchors || !showEntities;
    return { id: e.id, hidden };
  });
  allEdges.update(edgeUpdates);
}

["tog-wiki-links","tog-entities","tog-entity-links","tog-anchors"].forEach(id =>
  document.getElementById(id).addEventListener("change", applyToggles)
);

// ── ツールチップ & クリック ───────────────────────────────────────────────────
const tooltip = document.getElementById("tooltip");
const detail  = document.getElementById("detail");

network.on("hoverNode", ({ node, event }) => {
  const n = allNodes.get(node);
  tooltip.textContent = n.label;
  tooltip.style.display = "block";
  tooltip.style.left = (event.clientX + 14) + "px";
  tooltip.style.top  = (event.clientY - 10) + "px";
});
network.on("blurNode", () => { tooltip.style.display = "none"; });

network.on("click", ({ nodes: sel }) => {
  if (!sel.length) { detail.innerHTML = "ノードをクリックして詳細を表示"; return; }
  const n = allNodes.get(sel[0]);
  if (n.kind === "page") {
    detail.innerHTML = `<strong>${n.label}</strong><br>`
      + `<span style="color:#475569">種別: ${n.pageType || "—"}</span><br>`
      + `<span style="color:#475569">サブドメイン: ${n.subdomain || "—"}</span>`;
    // ダブルクリックで wiki ページを開く
  } else {
    detail.innerHTML = `<strong>${n.label}</strong><br>`
      + (n.wiki ? `<span style="color:#475569">← ${n.wiki}</span><br>` : "")
      + (n.description ? `<br>${n.description}` : "");
  }
});
network.on("doubleClick", ({ nodes: sel }) => {
  if (!sel.length) return;
  const n = allNodes.get(sel[0]);
  if (n.kind === "page") window.open("wiki/" + n.id + ".md", "_blank");
});

// ── ページクリックで関連エンティティをハイライト ──────────────────────────────
network.on("selectNode", ({ nodes: sel }) => {
  if (!sel.length) return;
  const n = allNodes.get(sel[0]);
  if (n.kind !== "page") return;
  // そのページに属するエンティティを強調
  const related = ENT_NODES.filter(e => e.wiki === n.id).map(e => e.id);
  if (related.length) network.selectNodes([n.id, ...related]);
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

    html = HTML
    html = html.replace("PAGE_NODES_JSON",  json.dumps(page_nodes,   ensure_ascii=False))
    html = html.replace("PAGE_EDGES_JSON",  json.dumps(page_edges,   ensure_ascii=False))
    html = html.replace("ENT_NODES_JSON",   json.dumps(ent_vis,      ensure_ascii=False))
    html = html.replace("ENT_EDGES_JSON",   json.dumps(ent_edge_vis, ensure_ascii=False))
    html = html.replace("ANCHOR_EDGES_JSON",json.dumps(anchor_edges, ensure_ascii=False))
    html = html.replace("STATS_TEXT", stats)

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"生成: {OUTPUT}")
    webbrowser.open(OUTPUT.as_uri())


if __name__ == "__main__":
    asyncio.run(main())
