import { useState } from 'react';
import { Save, Database, Shield, Sliders } from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export function Settings() {
  const [useMock, setUseMock] = useState(import.meta.env.VITE_USE_MOCK !== 'false');
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');
  const [ocrThreshold, setOcrThreshold] = useState(80);
  const [riskSensitivity, setRiskSensitivity] = useState('STANDARD');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Topbar title="Settings" subtitle="System preferences and API configurations" />

      <main className="flex-1 p-6 max-w-4xl w-full mx-auto space-y-6">
        {saved && (
          <div className="p-4 bg-risk-low-light border border-risk-low/30 rounded-lg text-xs font-medium text-risk-low">
            Settings saved successfully.
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* API & Data Source Config */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-surface-200">
              <Database className="h-5 w-5 text-brand-600" />
              <div>
                <h2 className="text-base font-semibold text-charcoal">API & Pipeline Integration</h2>
                <p className="text-xs text-charcoal-muted">
                  Configure backend connection for OCR, classification, extraction & risk engines
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-charcoal-secondary mb-1">
                  Backend API Endpoint Base URL
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="input-field w-full text-sm font-mono"
                  placeholder="http://localhost:8000"
                />
              </div>

              <div className="flex items-center justify-between p-3 bg-surface-50 rounded-md border border-surface-200">
                <div>
                  <p className="text-sm font-medium text-charcoal">Use Mock Data Mode</p>
                  <p className="text-xs text-charcoal-muted">
                    When enabled, frontend uses built-in realistic mock backend responses
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={useMock}
                  onChange={(e) => setUseMock(e.target.checked)}
                  className="h-4 w-4 text-brand-600 rounded focus:ring-brand-500 cursor-pointer"
                />
              </div>
            </div>
          </Card>

          {/* Verification Thresholds */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-surface-200">
              <Sliders className="h-5 w-5 text-brand-600" />
              <div>
                <h2 className="text-base font-semibold text-charcoal">Verification Thresholds</h2>
                <p className="text-xs text-charcoal-muted">
                  Set confidence thresholds for automated flag generation
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-medium text-charcoal-secondary">
                    OCR Confidence Warning Threshold
                  </label>
                  <span className="text-xs font-bold text-charcoal">{ocrThreshold}%</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="95"
                  value={ocrThreshold}
                  onChange={(e) => setOcrThreshold(Number(e.target.value))}
                  className="w-full h-2 bg-surface-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
                />
                <p className="text-xs text-charcoal-muted mt-1">
                  Documents with confidence below this score will flag low quality warnings.
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium text-charcoal-secondary mb-1">
                  Risk Sensitivity Level
                </label>
                <select
                  value={riskSensitivity}
                  onChange={(e) => setRiskSensitivity(e.target.value)}
                  className="input-field w-full text-sm"
                >
                  <option value="CONSERVATIVE font">Strict / Conservative (Higher flag sensitivity)</option>
                  <option value="STANDARD">Standard Enterprise Risk Rules</option>
                  <option value="LENIENT">Lenient (Fewer flagged mismatches)</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Compliance & Security */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-surface-200">
              <Shield className="h-5 w-5 text-brand-600" />
              <div>
                <h2 className="text-base font-semibold text-charcoal">Human-in-the-Loop & Audit</h2>
                <p className="text-xs text-charcoal-muted">
                  Module 8 compliance settings for loan officer approvals
                </p>
              </div>
            </div>

            <div className="text-xs text-charcoal-secondary space-y-2">
              <p className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-risk-low"></span>
                <span>AI Recommendation engine operates strictly in advisory mode.</span>
              </p>
              <p className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-risk-low"></span>
                <span>All approvals or rejections require manual officer confirmation with audit notes.</span>
              </p>
            </div>
          </Card>

          <div className="flex justify-end">
            <Button type="submit" icon={Save}>
              Save Preferences
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
