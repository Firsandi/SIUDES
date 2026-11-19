<?php

declare(strict_types=1);

header('Content-Type: application/json');

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($uri === '/api/unit/health' || $uri === '/health') {
    echo json_encode([
        'success' => true,
        'data' => [
            'status' => 'ok',
            'service' => 'unit-service',
        ],
        'error' => null,
    ]);
    exit;
}

http_response_code(404);
echo json_encode([
    'success' => false,
    'data' => null,
    'error' => [
        'code' => 'NOT_FOUND',
        'message' => 'Endpoint not found',
    ],
]);
