# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "cognee>=0.5.3",
#   "langfuse>=2.32.0,<3",
#   "python-dotenv>=1.0",
# ]
# ///
"""cognee のナレッジグラフに対してクエリを実行する"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import cognee  # noqa: E402

DATA_DIR = Path(__file__).parent / ".data"


async def main(query: str) -> None:
    cognee.config.data_root_directory(str(DATA_DIR))
    cognee.config.set_llm_api_key(os.environ["OPENAI_API_KEY"])
    cognee.config.set_llm_provider("openai")
    cognee.config.set_llm_model("gpt-4.1")

    results = await cognee.search(query_text=query)
    if not results:
        print("結果なし")
        return
    for i, r in enumerate(results, 1):
        # cognee は辞書またはオブジェクトを返す
        if isinstance(r, dict):
            text = r.get("text") or r.get("content") or r.get("name") or str(r)
        else:
            text = getattr(r, "text", None) or getattr(r, "content", None) or str(r)
        print(f"[{i}] {text}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: uv run search.py <クエリ>")
        sys.exit(1)
    asyncio.run(main(" ".join(sys.argv[1:])))
