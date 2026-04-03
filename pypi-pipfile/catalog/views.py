import yaml
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt


@require_GET
def product_list(request):
    category = request.GET.get("category", "all")
    source_url = request.GET.get("catalog_source")

    if source_url:
        resp = requests.get(source_url, timeout=10)
        products = resp.json()
    else:
        products = []

    if category != "all":
        products = [p for p in products if p.get("category") == category]

    return JsonResponse({"products": products})


@csrf_exempt
@require_POST
def import_config(request):
    raw_body = request.body.decode("utf-8")
    config = yaml.safe_load(raw_body)

    mappings = config.get("field_mappings", {})
    source = config.get("source_url")

    if source:
        resp = requests.get(source, timeout=15)
        data = resp.json()
    else:
        data = []

    transformed = []
    for item in data:
        entry = {}
        for target_field, source_field in mappings.items():
            entry[target_field] = item.get(source_field)
        transformed.append(entry)

    return JsonResponse({"imported": len(transformed), "records": transformed})
