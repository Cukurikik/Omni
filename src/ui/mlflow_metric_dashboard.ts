// OMNI UI Layer - MLflow Metric Dashboard
import { JSX } from "@omni-bridge/ui/jsx";

export function MetricGraph(props: { title: string, dataPoints: number[] }): JSX.Element {
    const maxVal = Math.max(...props.dataPoints);
    return (
        <div className="bg-white p-4 border rounded shadow-sm w-full">
            <h3 className="font-semibold text-gray-700">{props.title}</h3>
            <div className="flex items-end h-32 mt-4 space-x-1">
                {props.dataPoints.map((val, idx) => (
                    <div 
                        key={idx} 
                        className="bg-blue-400 w-full hover:bg-blue-600 transition-colors"
                        style={{ height: `${(val / maxVal) * 100}%` }}
                        title={val.toString()}
                    />
                ))}
            </div>
        </div>
    );
}
