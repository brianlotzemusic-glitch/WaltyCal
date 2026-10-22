"""Offline test: python3 tools/test_etsy_ai.py (no network, no Etsy calls)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etsy
ai = {"description": "x\n\nDesigned with the help of digital and AI tools, and checked by hand."}
hand = {"description": "x\n\nDesigned by Duskwood Designs Co, drawn with digital tools and checked by hand."}
assert "tick" in etsy.ai_note(ai) and "no AI" not in etsy.ai_note(ai)
assert "no AI tools" in etsy.ai_note(hand)
assert "no AI tools" in etsy.ai_note({**ai, "ai_generated": False})
assert "tick" in etsy.ai_note({**hand, "ai_generated": True})
print("ok")
