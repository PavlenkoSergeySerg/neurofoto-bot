"""ВАХТЁР 2: не даёт закоммитить файлы-секреты (.env, *.pem, *.key и т.п.).
Кроссплатформенная замена bash-хука из МАСТЕР-ДОКУМЕНТА (раздел 4):
на Windows без Git Bash команда bash -c не работает, python — работает везде.
"""
import re
import subprocess
import sys

# Чтобы pre-commit читал кириллицю без кракозябр (инцидент 10.09.2026)
sys.stdout.reconfigure(encoding="utf-8")

# Запрещённые имена файлов (маски раздела 4 МАСТЕР-ДОКУМЕНТА,
# НО с исключением: .env.example — контракт, его коммитить МОЖНО)
PATTERN = re.compile(
    r"(^|/)\.env($|/|\.(?!example$))"  # .env, .env.local, .env/... но НЕ .env.example
    r"|\.pem$"                         # сертификаты
    r"|\.key$"                         # приватные ключи
    r"|credentials.*\.json$"          # credentials.json, service-account*.json
    r"|token\.json$"
    r"|\.mcp\.json$",                 # конфиг MCP с токенами
    re.IGNORECASE,
)

def main() -> int:
    # Список файлов, подготовленных к коммиту (stage)
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=True,
    )
    bad = [name for name in out.stdout.splitlines() if PATTERN.search(name)]
    if bad:
        print("ERROR: попытка закоммитить чувствительные файлы:")
        for name in bad:
            print("  -", name)
        return 1  # ненулевой код выхода = commit отменён
    return 0

if __name__ == "__main__":
    sys.exit(main())