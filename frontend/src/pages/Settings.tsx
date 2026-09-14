import { useState } from 'react';
import { Save, Sliders } from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { Button } from '../components/ui/Button';

export function Settings() {
  const [ocrThreshold, setOcrThreshold] = useState(80);
  const [riskSensitivity, setRiskSensitivity] = useState('STANDARD');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#0A0A0A' }}>
      <Topbar title="Settings & Configurations" subtitle="System preferences, model thresholds & API configurations" />

      <main className="flex-1 p-6 max-w-4xl w-full mx-auto space-y-6 animate-fade-in">
        {saved && (
          <div
            className="p-4 rounded-xl text-xs font-medium"
            style={{
              background: 'rgba(52,199,89,0.1)',
              border: '1px solid rgba(52,199,89,0.3)',
              color: '#34C759',
            }}
          >
            Settings saved successfully.
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">

          {/* Verification Thresholds */}
          <div
            className="p-6 rounded-2xl"
            style={{
              background: '#111111',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div
              className="flex items-center gap-3 mb-5 pb-4"
              style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
            >
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: 'rgba(170,255,0,0.1)', color: '#AAFF00' }}
              >
                <Sliders className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>
                  Verification Thresholds
                </h2>
                <p className="text-xs" style={{ color: '#666666' }}>
                  Set confidence thresholds for automated flag generation
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-xs font-medium" style={{ color: '#888888' }}>
                    OCR Confidence Warning Threshold
                  </label>
                  <span className="text-xs font-bold" style={{ color: '#AAFF00' }}>
                    {ocrThreshold}%
                  </span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="95"
                  value={ocrThreshold}
                  onChange={(e) => setOcrThreshold(Number(e.target.value))}
                  className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-[#AAFF00]"
                  style={{ background: '#222222' }}
                />
                <p className="text-xs mt-1.5" style={{ color: '#666666' }}>
                  Documents with confidence below this score will flag low quality warnings.
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: '#888888' }}>
                  Risk Sensitivity Level
                </label>
                <select
                  value={riskSensitivity}
                  onChange={(e) => setRiskSensitivity(e.target.value)}
                  className="w-full text-sm px-3.5 py-2.5 rounded-xl transition-all focus:outline-none"
                  style={{
                    background: '#161616',
                    border: '1px solid rgba(255,255,255,0.08)',
                    color: '#F0F0F0',
                  }}
                >
                  <option value="CONSERVATIVE">Strict / Conservative (Higher flag sensitivity)</option>
                  <option value="STANDARD">Standard Enterprise Risk Rules</option>
                  <option value="LENIENT">Lenient (Fewer flagged mismatches)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button type="submit" icon={Save}>
              Save Preferences
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
