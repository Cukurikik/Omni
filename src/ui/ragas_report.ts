// OMNI UI Layer - RAGAS Report
import { JSX } from "@omni-bridge/ui/jsx";

type ReportState = {
    query: string;
    score: number;
};

export function RAGASReportView(props: { state: ReportState }): JSX.Element {
    const isPassing = props.state.score >= 0.8;
    
    return (
        <div className="ragas-report border p-4 rounded shadow-lg">
            <h3>Evaluation Report</h3>
            <div className="query-box text-sm text-gray-500">Query: {props.state.query}</div>
            <div className={`score-box ${isPassing ? 'text-green-600' : 'text-red-600'}`}>
                Faithfulness: {(props.state.score * 100).toFixed(1)}%
            </div>
        </div>
    );
}
