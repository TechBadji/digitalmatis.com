<?php
/**
 * DigitalMatis — Auto-deploy webhook
 * Déclenché par GitHub à chaque git push sur main
 * Test deploy : 2026-03-26
 */

// ─── Secret partagé avec GitHub ──────────────────
define('WEBHOOK_SECRET', 'dm_deploy_2026_Xk9pQr7vTzL4nW2j');

// ─── Vérification de la signature GitHub ─────────
$payload    = file_get_contents('php://input');
$sigHeader  = $_SERVER['HTTP_X_HUB_SIGNATURE_256'] ?? '';
$expected   = 'sha256=' . hash_hmac('sha256', $payload, WEBHOOK_SECRET);

if (!hash_equals($expected, $sigHeader)) {
    http_response_code(401);
    die('Unauthorized');
}

// ─── Vérification de l'événement (push uniquement) ─
$event = $_SERVER['HTTP_X_GITHUB_EVENT'] ?? '';
if ($event !== 'push') {
    http_response_code(200);
    die('Event ignored: ' . $event);
}

// ─── Vérification de la branche (main uniquement) ──
$data   = json_decode($payload, true);
$branch = $data['ref'] ?? '';
if ($branch !== 'refs/heads/main') {
    http_response_code(200);
    die('Branch ignored: ' . $branch);
}

// ─── Déclenchement du deploy site ────────────────
$output = shell_exec('sudo /usr/bin/git -C /opt/bitnami/apache/htdocs pull origin main 2>&1');

// ─── Mise à jour des dépendances bot si besoin ───
$pipOutput = shell_exec('cd /opt/bitnami/apache/htdocs/trading-bot && /home/bitnami/trading-bot-venv/bin/pip install -q -r requirements.txt 2>&1');

// ─── Redémarrage du bot trading ──────────────────
$botOutput = shell_exec('sudo /bin/systemctl restart trading-bot 2>&1');

// ─── Log ──────────────────────────────────────────
$logLine = '[' . date('Y-m-d H:i:s') . '] DEPLOY OK' . PHP_EOL
         . 'Site: ' . $output . PHP_EOL
         . 'Bot restart: ' . $botOutput . PHP_EOL;
file_put_contents('/opt/bitnami/apache/htdocs/deploy.log', $logLine, FILE_APPEND);

http_response_code(200);
echo 'Deployed: ' . $output;
