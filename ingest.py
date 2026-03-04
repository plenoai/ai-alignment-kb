# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "cognee>=0.5.3",
#   "langfuse>=2.32.0,<3",
#   "python-dotenv>=1.0",
# ]
# ///
"""wiki/ の Markdown ファイルを cognee に投入してナレッジグラフを構築する"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import cognee  # noqa: E402

DATA_DIR = Path(__file__).parent / ".data"
WIKI_DIR = Path(__file__).parent / "wiki"
SKIP_PREFIXES = ("tag-", "index")


def wiki_pages() -> list[Path]:
    return [
        p
        for p in sorted(WIKI_DIR.glob("*.md"))
        if not any(p.name.startswith(prefix) for prefix in SKIP_PREFIXES)
    ]


async def main() -> None:
    cognee.config.data_root_directory(str(DATA_DIR))
    cognee.config.set_llm_api_key(os.environ["OPENAI_API_KEY"])
    cognee.config.set_llm_provider("openai")
    cognee.config.set_llm_model("gpt-4.1")

    print("cognee をリセット中...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    pages = wiki_pages()
    print(f"{len(pages)} ページを投入します")

    for page in pages:
        text = page.read_text(encoding="utf-8")
        await cognee.add(text, dataset_name=page.stem)
        print(f"  追加: {page.name}")

    print("ナレッジグラフを構築中（cognify）...")
    await cognee.cognify()
    print("完了")


if __name__ == "__main__":
    asyncio.run(main())
