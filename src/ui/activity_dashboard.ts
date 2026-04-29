// OMNI UI Layer - Activity Dashboard
import { JSX } from "@omni-bridge/ui/jsx";

type ActivityState = {
    currentActivity: string;
    confidence: number;
    sensorActive: boolean;
};

export function ActivityDashboard(props: { state: ActivityState }): JSX.Element {
    return (
        <div className="activity-dashboard p-4 bg-gray-100 rounded-xl shadow-md">
            <h2 className="text-xl font-bold mb-4">SensorLLM Human Activity Recognition</h2>
            <div className="flex items-center space-x-4">
                <div className={`status-dot w-4 h-4 rounded-full ${props.state.sensorActive ? 'bg-green-500' : 'bg-red-500'}`} />
                <div className="text-lg">
                    Detected: <span className="font-semibold text-blue-600">{props.state.currentActivity}</span>
                </div>
            </div>
            <div className="mt-2 text-sm text-gray-500">
                Confidence: {(props.state.confidence * 100).toFixed(1)}%
            </div>
        </div>
    );
}
