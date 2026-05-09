<?php
/**
 * OmniWebhookProcessor.php — Webhook Processor for Model Events
 * Inspired by: CI/CD pipeline event handling for OMNI model lifecycle
 * Layer: Domain / PHP
 *
 * Processes webhook events for model training completion,
 * deployment triggers, and health alerts with retry logic.
 */

declare(strict_types=1);

namespace Omni\Domain\Webhook;

class WebhookEvent
{
    public readonly string $eventId;
    public readonly string $eventType;
    public readonly string $source;
    public readonly array $payload;
    public readonly string $signature;
    public readonly \DateTimeImmutable $receivedAt;
    public readonly int $retryCount;

    public function __construct(
        string $eventType,
        string $source,
        array $payload,
        string $signature = '',
        int $retryCount = 0
    ) {
        $this->eventId = bin2hex(random_bytes(12));
        $this->eventType = $eventType;
        $this->source = $source;
        $this->payload = $payload;
        $this->signature = $signature;
        $this->receivedAt = new \DateTimeImmutable();
        $this->retryCount = $retryCount;
    }
}

enum EventType: string
{
    case TrainingComplete = 'training.complete';
    case TrainingFailed = 'training.failed';
    case ValidationPassed = 'validation.passed';
    case ValidationFailed = 'validation.failed';
    case DeploymentStarted = 'deployment.started';
    case DeploymentComplete = 'deployment.complete';
    case DeploymentFailed = 'deployment.failed';
    case HealthAlert = 'health.alert';
    case ModelRegistered = 'model.registered';
    case MetricThreshold = 'metric.threshold';
}

class ProcessingResult
{
    public readonly bool $success;
    public readonly string $message;
    public readonly ?array $actions;

    public function __construct(bool $success, string $message, ?array $actions = null)
    {
        $this->success = $success;
        $this->message = $message;
        $this->actions = $actions;
    }
}

interface WebhookHandler
{
    public function canHandle(WebhookEvent $event): bool;
    public function handle(WebhookEvent $event): ProcessingResult;
}

class TrainingCompleteHandler implements WebhookHandler
{
    public function canHandle(WebhookEvent $event): bool
    {
        return $event->eventType === EventType::TrainingComplete->value;
    }

    public function handle(WebhookEvent $event): ProcessingResult
    {
        $modelName = $event->payload['model_name'] ?? 'unknown';
        $metrics = $event->payload['metrics'] ?? [];
        $accuracy = $metrics['accuracy'] ?? 0;
        $loss = $metrics['final_loss'] ?? 0;

        $actions = [];

        if ($accuracy >= 0.95) {
            $actions[] = ['type' => 'auto_deploy', 'model' => $modelName, 'env' => 'staging'];
            $actions[] = ['type' => 'notify', 'channel' => 'team', 'msg' => "Model {$modelName} achieved {$accuracy} accuracy"];
        } elseif ($accuracy >= 0.90) {
            $actions[] = ['type' => 'schedule_validation', 'model' => $modelName];
            $actions[] = ['type' => 'notify', 'channel' => 'team', 'msg' => "Model {$modelName} ready for review"];
        } else {
            $actions[] = ['type' => 'flag_review', 'model' => $modelName, 'reason' => 'low_accuracy'];
        }

        return new ProcessingResult(true, "Processed training completion for {$modelName}", $actions);
    }
}

class DeploymentHandler implements WebhookHandler
{
    public function canHandle(WebhookEvent $event): bool
    {
        return str_starts_with($event->eventType, 'deployment.');
    }

    public function handle(WebhookEvent $event): ProcessingResult
    {
        $modelName = $event->payload['model_name'] ?? 'unknown';
        $environment = $event->payload['environment'] ?? 'unknown';
        $version = $event->payload['version'] ?? '0.0.0';

        $actions = match ($event->eventType) {
            EventType::DeploymentComplete->value => [
                ['type' => 'health_check', 'model' => $modelName, 'env' => $environment],
                ['type' => 'update_registry', 'model' => $modelName, 'version' => $version, 'status' => 'deployed'],
                ['type' => 'notify', 'channel' => 'ops', 'msg' => "Deployed {$modelName} v{$version} to {$environment}"],
            ],
            EventType::DeploymentFailed->value => [
                ['type' => 'rollback', 'model' => $modelName, 'env' => $environment],
                ['type' => 'alert', 'severity' => 'high', 'msg' => "Deployment failed: {$modelName} v{$version}"],
            ],
            default => [
                ['type' => 'log', 'event' => $event->eventType],
            ],
        };

        return new ProcessingResult(true, "Handled {$event->eventType} for {$modelName}", $actions);
    }
}

class HealthAlertHandler implements WebhookHandler
{
    public function canHandle(WebhookEvent $event): bool
    {
        return $event->eventType === EventType::HealthAlert->value;
    }

    public function handle(WebhookEvent $event): ProcessingResult
    {
        $severity = $event->payload['severity'] ?? 'info';
        $component = $event->payload['component'] ?? 'unknown';
        $message = $event->payload['message'] ?? '';

        $actions = [];

        switch ($severity) {
            case 'critical':
                $actions[] = ['type' => 'page_oncall', 'component' => $component];
                $actions[] = ['type' => 'auto_scale', 'component' => $component, 'direction' => 'up'];
                break;
            case 'warning':
                $actions[] = ['type' => 'notify', 'channel' => 'ops', 'msg' => "Warning: {$component} - {$message}"];
                break;
            case 'info':
                $actions[] = ['type' => 'log', 'component' => $component, 'msg' => $message];
                break;
        }

        return new ProcessingResult(true, "Health alert processed: {$severity} on {$component}", $actions);
    }
}

class OmniWebhookProcessor
{
    /** @var WebhookHandler[] */
    private array $handlers = [];
    private array $processedEvents = [];
    private string $signingSecret;
    private int $maxRetries;

    public function __construct(string $signingSecret = '', int $maxRetries = 3)
    {
        $this->signingSecret = $signingSecret;
        $this->maxRetries = $maxRetries;

        // Register default handlers
        $this->registerHandler(new TrainingCompleteHandler());
        $this->registerHandler(new DeploymentHandler());
        $this->registerHandler(new HealthAlertHandler());
    }

    public function registerHandler(WebhookHandler $handler): void
    {
        $this->handlers[] = $handler;
    }

    public function process(WebhookEvent $event): ProcessingResult
    {
        // Verify signature if secret is configured
        if ($this->signingSecret !== '' && !$this->verifySignature($event)) {
            return new ProcessingResult(false, 'Invalid webhook signature');
        }

        // Deduplicate
        if (isset($this->processedEvents[$event->eventId])) {
            return new ProcessingResult(true, 'Event already processed (deduplicated)');
        }

        // Find matching handler
        foreach ($this->handlers as $handler) {
            if ($handler->canHandle($event)) {
                $result = $handler->handle($event);
                $this->processedEvents[$event->eventId] = [
                    'event' => $event,
                    'result' => $result,
                    'processed_at' => new \DateTimeImmutable(),
                ];
                return $result;
            }
        }

        return new ProcessingResult(false, "No handler found for event type: {$event->eventType}");
    }

    private function verifySignature(WebhookEvent $event): bool
    {
        if (empty($event->signature)) {
            return false;
        }

        $payload = json_encode($event->payload);
        $expected = hash_hmac('sha256', $payload, $this->signingSecret);
        return hash_equals($expected, $event->signature);
    }

    public function getProcessedCount(): int
    {
        return count($this->processedEvents);
    }

    public function getRecentEvents(int $limit = 10): array
    {
        return array_slice($this->processedEvents, -$limit, $limit, true);
    }
}
