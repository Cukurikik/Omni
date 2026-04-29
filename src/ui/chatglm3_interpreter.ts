// OMNI UI Layer - ChatGLM3 Interpreter
import { JSX } from "@omni-bridge/ui/jsx";

export function CodeInterpreter(props: { code: string, output: string }): JSX.Element {
    return (
        <div className="interpreter bg-gray-900 font-mono p-4 rounded text-sm text-gray-300">
            <div className="mb-2 flex justify-between border-b border-gray-700 pb-2">
                <span className="text-blue-400">Code Execution</span>
                <span className="text-green-400">Success</span>
            </div>
            <pre className="text-yellow-300 mb-4 overflow-x-auto">
                {props.code}
            </pre>
            <div className="bg-black p-2 rounded border border-gray-800">
                <span className="text-gray-500">Output:</span>
                <pre className="mt-1">{props.output}</pre>
            </div>
        </div>
    );
}
