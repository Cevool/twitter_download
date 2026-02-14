import argparse
import json
import os
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Control manual start time for likes sync state.")
    parser.add_argument("action", choices=["set-start", "clear-start", "show"])
    parser.add_argument("--user", default="ars_0947", help="X screen name without @")
    parser.add_argument(
        "--time",
        default="",
        help='Manual start time, format "YYYY-MM-DD HH:MM" or "YYYY-MM-DD"',
    )
    parser.add_argument("--state-dir", default="./state", help="State directory path")
    return parser.parse_args()


def valid_time(value: str):
    value = (value or "").strip()
    if not value:
        return False
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def load_state(path: str):
    data = {
        "last_cursor": "",
        "last_seen_tweet_id": "",
        "last_run_time": "",
        "manual_start_time": "",
    }
    if not os.path.exists(path):
        return data
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        data.update(raw)
    return data


def save_state(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    args = parse_args()
    state_file = os.path.join(args.state_dir, f"{args.user}.state.json")
    state = load_state(state_file)

    if args.action == "set-start":
        if not valid_time(args.time):
            raise SystemExit('Invalid --time. Use "YYYY-MM-DD HH:MM" or "YYYY-MM-DD".')
        state["manual_start_time"] = args.time.strip()
        save_state(state_file, state)
        print(f"[OK] manual_start_time set to: {state['manual_start_time']}")
    elif args.action == "clear-start":
        state["manual_start_time"] = ""
        save_state(state_file, state)
        print("[OK] manual_start_time cleared")
    else:
        print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
