import requests


def main():
    with requests.Session() as session:
        request = requests.Request(
            "GET", "https://example.invalid/inventory", params={"warehouse": "primary"}
        )
        prepared = session.prepare_request(request)
        print(f"{prepared.method} {prepared.url}")


if __name__ == "__main__":
    main()
