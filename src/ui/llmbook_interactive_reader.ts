// OMNI UI Layer - LLMBook Interactive Reader
import { JSX } from "@omni-bridge/ui/jsx";

export function LLMBookReader(props: { chapterTitle: string, content: string }): JSX.Element {
    return (
        <div className="llm-book max-w-4xl mx-auto my-8 bg-white text-gray-900 p-10 shadow-2xl rounded-lg font-serif">
            <h1 className="text-3xl font-extrabold border-b-2 border-indigo-500 pb-4 mb-6">
                {props.chapterTitle}
            </h1>
            <div className="prose prose-indigo lg:prose-lg max-w-none leading-relaxed">
                <p>{props.content}</p>
            </div>
            <div className="mt-8 flex justify-between text-sm text-indigo-600 font-bold">
                <button>← Previous Chapter</button>
                <button>Next Chapter →</button>
            </div>
        </div>
    );
}
