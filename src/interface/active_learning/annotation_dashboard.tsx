import React, { useState } from 'react';

interface AnnotationTask {
  id: string;
  data: string;
  uncertainty: number;
}

export const AnnotationDashboard: React.FC = () => {
  const [tasks] = useState<AnnotationTask[]>([
    { id: 't1', data: 'The model is highly unsure about this image.', uncertainty: 0.95 },
    { id: 't2', data: 'Is this a malicious packet or normal traffic?', uncertainty: 0.88 },
    { id: 't3', data: 'Boundary detection failed here.', uncertainty: 0.82 }
  ]);

  const [currentIndex, setCurrentIndex] = useState(0);

  const handleLabel = (label: string) => {
    console.log(`Labeled ${tasks[currentIndex].id} as ${label}`);
    if (currentIndex < tasks.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      alert("All tasks completed!");
    }
  };

  if (currentIndex >= tasks.length) {
    return <div className="p-8 text-center text-green-600 font-bold">Queue Empty. Great job!</div>;
  }

  const currentTask = tasks[currentIndex];

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md border border-gray-200">
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <h2 className="text-xl font-bold text-gray-800">Human-in-the-Loop Annotation</h2>
        <span className="bg-red-100 text-red-800 text-xs font-semibold px-2.5 py-0.5 rounded">
          High Uncertainty: {currentTask.uncertainty.toFixed(2)}
        </span>
      </div>

      <div className="mb-8 p-8 bg-gray-50 border border-gray-300 border-dashed rounded text-center">
        <p className="text-lg text-gray-700 italic">"{currentTask.data}"</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button 
          onClick={() => handleLabel('Positive')}
          className="py-3 bg-green-50 text-green-700 border border-green-200 rounded hover:bg-green-100 transition font-semibold"
        >
          Label Positive
        </button>
        <button 
          onClick={() => handleLabel('Negative')}
          className="py-3 bg-red-50 text-red-700 border border-red-200 rounded hover:bg-red-100 transition font-semibold"
        >
          Label Negative
        </button>
        <button 
          onClick={() => handleLabel('Skip')}
          className="col-span-2 py-2 bg-gray-100 text-gray-600 border border-gray-300 rounded hover:bg-gray-200 transition"
        >
          Skip (Low Confidence)
        </button>
      </div>
      
      <div className="mt-6 text-sm text-gray-500 text-center">
        Task {currentIndex + 1} of {tasks.length}
      </div>
    </div>
  );
};
