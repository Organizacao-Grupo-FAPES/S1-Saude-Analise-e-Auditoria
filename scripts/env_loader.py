import os
import re

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(PROJECT_DIR, ".env")

def load_dotenv():
    if not os.path.exists(ENV_PATH):
        return

    with open(ENV_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()

            # Se começar com [ ou { e não fechar na mesma linha, junta as linhas seguintes
            if (v.startswith("[") and not v.endswith("]")) or (v.startswith("{") and not v.endswith("}")):
                json_lines = [v]
                i += 1
                while i < len(lines):
                    subline = lines[i].strip()
                    json_lines.append(subline)
                    if (v.startswith("[") and subline.endswith("]")) or (v.startswith("{") and subline.endswith("}")):
                        break
                    i += 1
                v = "".join(json_lines)

            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]

            if k and k not in os.environ:
                os.environ[k] = v
        i += 1

load_dotenv()
