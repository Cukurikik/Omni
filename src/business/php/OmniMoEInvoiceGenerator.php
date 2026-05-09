<?php
/**
 * OMNI Framework - MoE API Invoice Generator (PHP)
 * Connects to the PostgreSQL Billing Ledger to generate monthly PDF
 * invoices detailing token usage and active parameter billing costs.
 */

require_once('vendor/autoload.php');

class OmniMoEInvoiceGenerator {
    private $db;

    public function __construct($dbHost, $dbName, $dbUser, $dbPass) {
        $dsn = "pgsql:host=$dbHost;dbname=$dbName";
        try {
            $this->db = new PDO($dsn, $dbUser, $dbPass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
            echo "OMNI PHP: Connected to Billing Ledger.\n";
        } catch (PDOException $e) {
            die("Database connection failed: " . $e->getMessage());
        }
    }

    public function generateMonthlyInvoice($tenantId, $month) {
        // Query the analytics view created in moe_billing_schema.sql
        $stmt = $this->db->prepare("
            SELECT total_tokens, avg_active_param_percentage, total_cost_usd
            FROM v_monthly_invoice
            WHERE tenant_id = :tenant_id AND invoice_month = :month
        ");
        
        $stmt->execute(['tenant_id' => $tenantId, 'month' => $month]);
        $data = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$data) {
            echo "OMNI PHP: No billing data found for tenant $tenantId in $month.\n";
            return;
        }

        $pdf = new TCPDF(PDF_PAGE_ORIENTATION, PDF_UNIT, PDF_PAGE_FORMAT, true, 'UTF-8', false);
        $pdf->SetCreator('OMNI Framework');
        $pdf->SetAuthor('Omni Billing Service');
        $pdf->SetTitle("Invoice - $tenantId - $month");
        $pdf->AddPage();

        $html = "
            <h1>OMNI MoE Cloud Services</h1>
            <h2>Invoice for $month</h2>
            <p><strong>Tenant ID:</strong> $tenantId</p>
            <hr>
            <h3>Usage Breakdown</h3>
            <table border=\"1\" cellpadding=\"5\">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Tokens Processed</td>
                    <td>" . number_format($data['total_tokens']) . "</td>
                </tr>
                <tr>
                    <td>Average Active MoE Parameters</td>
                    <td>" . number_format($data['avg_active_param_percentage'], 2) . "%</td>
                </tr>
                <tr>
                    <td><b>Total Cost (USD)</b></td>
                    <td><b>$" . number_format($data['total_cost_usd'], 2) . "</b></td>
                </tr>
            </table>
            <br><p>Thank you for using the OMNI Polyglot Platform.</p>
        ";

        $pdf->writeHTML($html, true, false, true, false, '');
        $outputPath = "/tmp/invoice_$tenantId.pdf";
        $pdf->Output($outputPath, 'F');
        
        echo "OMNI PHP: Invoice generated successfully at $outputPath\n";
    }
}

// Simulated Execution
// $generator = new OmniMoEInvoiceGenerator('localhost', 'omni_db', 'postgres', 'secret');
// $generator->generateMonthlyInvoice('123e4567-e89b-12d3-a456-426614174000', '2026-05-01');
