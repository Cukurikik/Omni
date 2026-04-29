// OMNI UI Layer - Test Report View
import { JSX } from "@omni-bridge/ui/jsx";

type ReportState = {
    testName: string;
    passed: boolean;
    relevanceScore: number;
};

export function ContextCheckReport(props: { state: ReportState }): JSX.Element {
    return (
        <div className={`report-card p-4 rounded ${props.state.passed ? 'bg-green-50' : 'bg-red-50'}`}>
            <h3 className="font-bold text-lg">{props.state.testName}</h3>
            <div className="flex justify-between mt-2">
                <span>Status: {props.state.passed ? 'PASSED' : 'FAILED'}</span>
                <span>Context Score: {(props.state.relevanceScore * 100).toFixed(1)}%</span>
            </div>
        </div>
    );
}
