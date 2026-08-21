from hashlib import sha256
from pathlib import Path
import re

server = Path("internal/httpapi/server.go")
value = server.read_text()
value = value.replace(
    "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
)
server.write_text(value)

root = Path("internal/web/static")
if not root.exists():
    raise SystemExit(0)

bootstrap = root / "_app" / "bootstrap"
bootstrap.mkdir(parents=True, exist_ok=True)
pattern = re.compile(r"<script>(.*?)</script>", re.DOTALL)

for html in root.rglob("*.html"):
    source = html.read_text()

    def externalize(match: re.Match[str]) -> str:
        code = match.group(1).strip()
        if not code:
            return match.group(0)
        digest = sha256(code.encode()).hexdigest()[:20]
        target = bootstrap / f"{digest}.js"
        target.write_text(code + "\n")
        return f'<script src="/_app/bootstrap/{target.name}"></script>'

    html.write_text(pattern.sub(externalize, source))
