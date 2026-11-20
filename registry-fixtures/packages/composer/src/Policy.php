<?php
namespace ZeroPathRehearsal;
final class Policy {
    public static function version(): string {
        $logger = new \Psr\Log\NullLogger();
        $logger->info('policy fixture');
        return '1.0.0';
    }
}
