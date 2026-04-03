<?php

require __DIR__ . '/vendor/autoload.php';

use GuzzleHttp\Client;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\JsonResponse;

$request = Request::createFromGlobals();
$client = new Client(['timeout' => 10]);

$path = $request->getPathInfo();
$method = $request->getMethod();

if ($path === '/api/products' && $method === 'GET') {
    $sourceUrl = $request->query->get('source');
    if (!$sourceUrl) {
        (new JsonResponse(['error' => 'source parameter required'], 400))->send();
        exit;
    }

    try {
        $response = $client->get($sourceUrl);
        $products = json_decode($response->getBody()->getContents(), true);
        (new JsonResponse(['products' => $products]))->send();
    } catch (\Exception $e) {
        (new JsonResponse(['error' => 'Failed to fetch products'], 502))->send();
    }

} elseif ($path === '/api/webhook' && $method === 'POST') {
    $payload = json_decode($request->getContent(), true);
    $callbackUrl = $payload['callback_url'] ?? null;
    $eventData = $payload['event'] ?? [];

    if ($callbackUrl) {
        try {
            $client->post($callbackUrl, [
                'json' => [
                    'received_at' => date('c'),
                    'event' => $eventData,
                    'status' => 'processed',
                ],
            ]);
        } catch (\Exception $e) {
            error_log("Webhook callback failed: " . $e->getMessage());
        }
    }

    (new JsonResponse(['status' => 'accepted']))->send();

} elseif ($path === '/api/render' && $method === 'POST') {
    $data = json_decode($request->getContent(), true);
    $templateStr = $data['template'] ?? 'Hello {{ name }}';
    $context = $data['context'] ?? [];

    $loader = new \Twig\Loader\ArrayLoader(['notification' => $templateStr]);
    $twig = new \Twig\Environment($loader);
    $rendered = $twig->render('notification', $context);

    (new JsonResponse(['rendered' => $rendered]))->send();

} elseif ($path === '/health') {
    (new JsonResponse(['status' => 'ok']))->send();

} else {
    (new JsonResponse(['error' => 'Not found'], 404))->send();
}
