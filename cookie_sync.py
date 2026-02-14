import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Sync X cookie from local Chrome into .env")
    parser.add_argument("--env-file", default=".env", help="Target .env file path")
    return parser.parse_args()


def read_cookie_from_chrome():
    try:
        import browser_cookie3  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "browser-cookie3 is required. Install with: pip install browser-cookie3"
        ) from e

    jar = browser_cookie3.chrome()
    auth_token = ""
    ct0 = ""
    for c in jar:
        domain = (c.domain or "").lstrip(".")
        if domain.endswith("x.com") or domain.endswith("twitter.com"):
            if c.name == "auth_token":
                auth_token = c.value
            elif c.name == "ct0":
                ct0 = c.value
    if not auth_token or not ct0:
        raise RuntimeError("Cannot find auth_token/ct0 in Chrome cookies for x.com/twitter.com")
    return f"auth_token={auth_token}; ct0={ct0};"


def upsert_env(env_file: str, key: str, value: str):
    lines = []
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

    found = False
    for idx, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[idx] = f'{key}="{value}"'
            found = True
            break
    if not found:
        lines.append(f'{key}="{value}"')

    with open(env_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")


def main():
    args = parse_args()
    cookie = read_cookie_from_chrome()
    upsert_env(args.env_file, "TW_COOKIE", cookie)
    print(f"[OK] TW_COOKIE updated in {args.env_file}")


if __name__ == "__main__":
    main()
