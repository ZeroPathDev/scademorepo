import sys
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape


def load_template_env(template_dir="templates"):
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )


def fetch_inventory(api_base):
    resp = requests.get(f"{api_base}/api/inventory", timeout=10)
    resp.raise_for_status()
    return resp.json()


def generate_report(env, inventory_data, output_path):
    template = env.get_template("inventory_report.html")
    rendered = template.render(
        items=inventory_data["items"],
        total=inventory_data["total"],
        warehouse=inventory_data.get("warehouse", "main"),
    )
    with open(output_path, "w") as f:
        f.write(rendered)
    return output_path


def sync_upstream(api_base, records):
    for batch_start in range(0, len(records), 50):
        batch = records[batch_start : batch_start + 50]
        resp = requests.post(
            f"{api_base}/api/inventory/sync",
            json={"records": batch},
            timeout=30,
        )
        resp.raise_for_status()


def main():
    api_base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    env = load_template_env()

    inventory = fetch_inventory(api_base)
    report_path = generate_report(env, inventory, "report.html")
    print(f"Report written to {report_path}")

    if "--sync" in sys.argv:
        sync_upstream(api_base, inventory["items"])
        print("Upstream sync complete")


if __name__ == "__main__":
    main()
