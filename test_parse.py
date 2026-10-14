"""Offline checks for the parsing helpers: python3 test_parse.py"""
import importlib.machinery
import importlib.util
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slak")
loader = importlib.machinery.SourceFileLoader("slak", path)
slak = importlib.util.module_from_spec(importlib.util.spec_from_loader("slak", loader))
loader.exec_module(slak)

P = "https://x.slack.com/archives/C0000000001/p1700000000123456"
assert slak.parse_permalink(P) == ("C0000000001", "1700000000.123456")
assert slak.parse_permalink(P + "?thread_ts=1699999999.000100&cid=C0000000001") == \
    ("C0000000001", "1699999999.000100")
assert slak.parse_permalink("#random") is None


class FakeClient:
    def user_name(self, uid):
        return {"U1": "alice"}.get(uid, uid)


t = "hi <@U1> see <#C1|random> <!here> <https://a.b/c?x=1&amp;y=2|a.b> &lt;3"
assert slak.plain(FakeClient(), t) == "hi @alice see #random @here https://a.b/c?x=1&y=2 <3", \
    slak.plain(FakeClient(), t)
# Cookie decryption round-trip through the same openssl call slak uses.
import hashlib, subprocess
pw, value = b"keyring-secret", b"xoxd-abc%2Fdef%3D"
key = hashlib.pbkdf2_hmac("sha1", pw, b"saltysalt", 1, 16)
plain = hashlib.sha256(b".slack.com").digest() + value
pad = 16 - len(plain) % 16
enc = subprocess.run(["openssl", "enc", "-aes-128-cbc", "-nopad", "-K", key.hex(), "-iv", "20" * 16],
                     input=plain + bytes([pad]) * pad, capture_output=True, check=True).stdout
assert slak.decrypt_cookie(enc, [b"wrong", pw], 1) == value.decode()
assert slak.decrypt_cookie(enc, [b"wrong"], 1) is None
print("ok")
