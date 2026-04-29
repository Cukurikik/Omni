// OMNI UI Layer - AI Academy Interactive Lesson
import { JSX } from "@omni-bridge/ui/jsx";

export function AcademyLessonCard(props: { title: string, progress: number }): JSX.Element {
    return (
        <div className="bg-white rounded-lg shadow p-6 max-w-sm border-t-4 border-indigo-600">
            <h3 className="text-xl font-bold text-gray-800 mb-2">{props.title}</h3>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: `${props.progress}%` }}></div>
            </div>
            <p className="text-sm text-gray-500 text-right">{props.progress}% Completed</p>
            <button className="mt-4 w-full bg-indigo-50 text-indigo-700 py-2 rounded font-semibold hover:bg-indigo-100 transition">
                Continue Learning
            </button>
        </div>
    );
}
