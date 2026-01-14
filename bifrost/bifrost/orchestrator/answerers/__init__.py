"""Lane answerers package.

NOTE: Do not import lane modules here.
Keep imports explicit at call sites to preserve file-level separation:
- on_device.py imports RAG modules
- cloud.py must not import any RAG modules
"""

__all__ = []
