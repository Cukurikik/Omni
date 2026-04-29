import React, { useState, useEffect } from 'react';

export const AvatarStudio: React.FC = () => {
  const [yaw, setYaw] = useState(0);
  const [pitch, setPitch] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [eyeBlink, setEyeBlink] = useState(1);

  useEffect(() => {
    let frame = 0;
    const loop = setInterval(() => {
      frame++;
      
      // Deterministic autonomous motion simulation math
      const autoYaw = Math.sin(frame * 0.05) * 30;
      const autoPitch = Math.cos(frame * 0.03) * 15;
      
      setYaw(autoYaw);
      setPitch(autoPitch);

      // Deterministic blinking math (every ~4 seconds at 30fps)
      if (frame % 120 < 5) {
        setEyeBlink(0); // closed
      } else {
        setEyeBlink(1); // open
      }
      
      // Deterministic speaking math based on frame
      if (frame % 60 < 20) {
        setIsSpeaking(true);
      } else {
        setIsSpeaking(false);
      }

    }, 33); // ~30 FPS

    return () => clearInterval(loop);
  }, []);

  return (
    <div className="bg-zinc-900 p-8 rounded-2xl border border-zinc-700 shadow-2xl max-w-md mx-auto">
      <div className="flex justify-between items-center mb-6 border-b border-zinc-800 pb-4">
        <h2 className="text-xl font-bold text-pink-400">Talking Head Studio</h2>
        <div className="bg-zinc-800 px-2 py-1 rounded text-xs text-zinc-400 font-mono">
          30 FPS LIVE
        </div>
      </div>

      <div className="bg-zinc-950 h-64 rounded-xl border border-zinc-800 flex items-center justify-center relative overflow-hidden mb-6 shadow-inner">
        {/* Animated Avatar Representation */}
        <div 
          className="relative transition-transform duration-[33ms] ease-linear"
          style={{ 
            transform: `perspective(600px) rotateY(${yaw}deg) rotateX(${-pitch}deg)`
          }}
        >
          {/* Head base */}
          <div className="w-32 h-40 bg-pink-100 rounded-[3rem_3rem_2rem_2rem] shadow-lg relative overflow-hidden border-2 border-pink-200">
            {/* Hair */}
            <div className="absolute top-0 w-full h-12 bg-pink-300 rounded-t-[3rem]"></div>
            
            {/* Eyes */}
            <div className="absolute top-16 w-full flex justify-between px-6">
              <div 
                className="w-5 bg-pink-900 rounded-full transition-all duration-[33ms]"
                style={{ height: `${eyeBlink * 14}px`, marginTop: `${(1-eyeBlink) * 7}px` }}
              ></div>
              <div 
                className="w-5 bg-pink-900 rounded-full transition-all duration-[33ms]"
                style={{ height: `${eyeBlink * 14}px`, marginTop: `${(1-eyeBlink) * 7}px` }}
              ></div>
            </div>

            {/* Mouth */}
            <div className="absolute bottom-8 w-full flex justify-center">
              <div 
                className="bg-red-400 transition-all duration-75"
                style={{
                  width: isSpeaking ? '24px' : '16px',
                  height: isSpeaking ? '16px' : '4px',
                  borderRadius: isSpeaking ? '8px 8px 12px 12px' : '2px'
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-zinc-800 p-3 rounded">
          <div className="text-xs text-zinc-500 uppercase">Yaw (RotY)</div>
          <div className="text-lg font-mono text-zinc-300">{yaw.toFixed(1)}°</div>
        </div>
        <div className="bg-zinc-800 p-3 rounded">
          <div className="text-xs text-zinc-500 uppercase">Pitch (RotX)</div>
          <div className="text-lg font-mono text-zinc-300">{pitch.toFixed(1)}°</div>
        </div>
      </div>
      
      <div className="bg-zinc-800 p-3 rounded flex justify-between items-center">
        <div className="text-xs text-zinc-500 uppercase">Morph State</div>
        <div className="text-xs font-mono text-teal-400">
          {isSpeaking ? 'SPEAKING' : 'IDLE'} | EYE_{eyeBlink === 1 ? 'OPEN' : 'CLOSED'}
        </div>
      </div>
    </div>
  );
};
