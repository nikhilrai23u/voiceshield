
import { useState } from "react";
import {
  ShieldCheck,
  AudioLines,
  Upload,
  LayoutDashboard,
  History,
  Settings,
  Activity,
  FileAudio,
  AlertTriangle,
  CheckCircle2,
  Menu,
  X,
} from "lucide-react";
import "./App.css";

export default function App() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [message, setMessage] = useState("");

  function handleFile(selectedFile) {
    if (!selectedFile) return;

    const allowedExtensions = [".wav", ".flac", ".ogg"];
    const extension = selectedFile.name
      .slice(selectedFile.name.lastIndexOf("."))
      .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setMessage("Please upload a WAV, FLAC, or OGG audio file.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setMessage("");
  }

  async function analyzeAudio() {
    if (!file) {
      setMessage("Upload an audio file first.");
      return;
    }

    setAnalyzing(true);
    setMessage("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://localhost:8000/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const detail = data.detail;
        throw new Error(
          typeof detail === "string"
            ? detail
            : "Audio analysis failed."
        );
      }

      setResult(data);

      setMessage(
        `Audio processed successfully! Duration: ${
          data.duration_seconds
        }s | Sample rate: ${data.sample_rate} Hz | ${
          data.features?.mfcc_coefficients ?? 0
        } MFCC coefficients extracted. AI detection is not integrated yet.`
      );
    } catch (error) {
      setMessage(
        error.message === "Failed to fetch"
          ? "Cannot reach the backend. Make sure FastAPI is running on port 8000."
          : error.message
      );
    } finally {
      setAnalyzing(false);
    }
  }

  function removeFile() {
    setFile(null);
    setResult(null);
    setMessage("");
  }

  return (
    <div className="app-shell">
      <aside
        className={`sidebar ${
          mobileMenu ? "sidebar-open" : ""
        }`}
      >
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h2>VoiceShield</h2>
            <span>AI THREAT INTELLIGENCE</span>
          </div>

          <button
            className="mobile-close"
            onClick={() => setMobileMenu(false)}
            aria-label="Close menu"
          >
            <X size={19} />
          </button>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>
          <a
            className="nav-item active"
            href="#dashboard"
            onClick={() => setMobileMenu(false)}
          >
            <LayoutDashboard size={19} />
            Dashboard
          </a>

          <a
            className="nav-item"
            href="#analysis"
            onClick={() => setMobileMenu(false)}
          >
            <AudioLines size={19} />
            Audio Analysis
          </a>

          <a
            className="nav-item"
            href="#history"
            onClick={() => setMobileMenu(false)}
          >
            <History size={19} />
            Scan History
          </a>

          <a
            className="nav-item"
            href="#settings"
            onClick={() => setMobileMenu(false)}
          >
            <Settings size={19} />
            Settings
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot" />

            <div>
              <strong>System online</strong>
              <p>
                {result
                  ? "Feature extraction available"
                  : "Detection model pending"}
              </p>
            </div>
          </div>

          <p className="sidebar-footer">
            CAPSTONE PROJECT · 2026–27
          </p>
        </div>
      </aside>

      {mobileMenu && (
        <button
          className="mobile-overlay"
          aria-label="Close navigation"
          onClick={() => setMobileMenu(false)}
        />
      )}

      <main className="main-area" id="dashboard">
        <header className="topbar">
          <button
            className="menu-button"
            onClick={() => setMobileMenu(true)}
            aria-label="Open menu"
          >
            <Menu size={22} />
          </button>

          <div className="breadcrumb">
            Workspace / <strong>Dashboard</strong>
          </div>

          <div className="topbar-right">
            <span className="environment">
              <span className="status-dot" />
              LOCAL ENVIRONMENT
            </span>

            <div className="avatar">VS</div>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome">
            <div>
              <div className="eyebrow">
                <Activity size={15} />
                VOICE AUTHENTICITY INTELLIGENCE
              </div>

              <h1>
                Audio Threat <span>Detection</span>
              </h1>

              <p>
                Analyze voice recordings and investigate
                potential synthetic speech attacks.
              </p>
            </div>

            <div className="secure-badge">
              <ShieldCheck size={17} />
              Security workspace
            </div>
          </section>

          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-top">
                <span>Audio analyzed</span>
                <FileAudio size={19} />
              </div>

              <div className="stat-value">
                {result ? "1" : "—"}
              </div>

              <p>
                {result
                  ? "Audio processed in this session"
                  : "Analyses will appear here"}
              </p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Threats detected</span>
                <AlertTriangle size={19} />
              </div>

              <div className="stat-value">—</div>

              <p>Awaiting model integration</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Detection accuracy</span>
                <Activity size={19} />
              </div>

              <div className="stat-value">—</div>

              <p>Requires model evaluation</p>
            </div>
          </section>

          <section className="analysis-layout" id="analysis">
            <div className="panel upload-panel">
              <div className="panel-heading">
                <div>
                  <h3>Analyze audio</h3>
                  <p>Upload a recording to prepare an analysis.</p>
                </div>

                <div className="panel-icon">
                  <AudioLines size={21} />
                </div>
              </div>

              <label className="dropzone">
                <input
                  type="file"
                  accept=".wav,.flac,.ogg,audio/wav,audio/flac,audio/ogg"
                  onChange={(event) =>
                    handleFile(event.target.files?.[0])
                  }
                  hidden
                />

                <div className="upload-icon">
                  <Upload size={25} />
                </div>

                <strong>Drop your audio here</strong>
                <span>or click to browse your computer</span>
                <small>WAV · FLAC · OGG</small>
              </label>

              {file && (
                <div className="selected-file">
                  <FileAudio size={20} />

                  <div className="file-details">
                    <strong>{file.name}</strong>
                    <span>
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </span>
                  </div>

                  <button
                    className="remove-file"
                    onClick={removeFile}
                    disabled={analyzing}
                  >
                    Remove
                  </button>
                </div>
              )}

              <button
                className="analyze-button"
                onClick={analyzeAudio}
                disabled={analyzing || !file}
              >
                <ShieldCheck size={19} />
                {analyzing
                  ? "Analyzing audio..."
                  : "Analyze audio"}
              </button>

              {message && (
                <p className="feedback" role="status">
                  {message}
                </p>
              )}

              <p className="privacy-note">
                Audio features are extracted by the backend.
                Voice-cloning classification is not available yet.
              </p>
            </div>

            <div className="panel results-panel">
              <div className="panel-heading">
                <div>
                  <h3>Detection results</h3>
                  <p>Analysis output and threat assessment.</p>
                </div>

                <span className="waiting-pill">
                  {result ? "FEATURES EXTRACTED" : "AWAITING MODEL"}
                </span>
              </div>

              <div className="empty-results">
                <div className="radar-icon">
                  <ShieldCheck size={36} />
                </div>

                <h4>
                  {result
                    ? "Audio analysis complete"
                    : "Ready for analysis"}
                </h4>

                <p>
                  {result
                    ? "Audio decoded and MFCC features extracted successfully."
                    : "Upload a recording and analyze it to see its audio properties here."}
                </p>

                <div className="result-divider" />

                <div className="result-row">
                  <span>Classification</span>
                  <strong>
                    {result?.classification ?? "Not available"}
                  </strong>
                </div>

                <div className="result-row">
                  <span>Risk score</span>
                  <strong>
                    {result?.risk_score ?? "Not available"}
                  </strong>
                </div>

                <div className="result-row">
                  <span>Confidence</span>
                  <strong>
                    {result?.confidence ?? "Not available"}
                  </strong>
                </div>

                <div className="result-divider" />

                <div className="result-row">
                  <span>Audio duration</span>
                  <strong>
                    {result
                      ? `${result.duration_seconds} seconds`
                      : "—"}
                  </strong>
                </div>

                <div className="result-row">
                  <span>Sample rate</span>
                  <strong>
                    {result ? `${result.sample_rate} Hz` : "—"}
                  </strong>
                </div>

                <div className="result-row">
                  <span>Channels</span>
                  <strong>
                    {result ? result.channels : "—"}
                  </strong>
                </div>

                {result?.features?.mfcc_mean && (
                  <>
                    <div className="result-divider" />

                    <h4>MFCC feature extraction</h4>

                    <p>
                      {result.features.mfcc_coefficients} coefficients
                      averaged across audio frames.
                    </p>

                    <div className="mfcc-list">
                      {result.features.mfcc_mean.map(
                        (value, index) => (
                          <div
                            className="result-row"
                            key={index}
                          >
                            <span>MFCC {index + 1}</span>
                            <strong>
                              {Number(value).toFixed(4)}
                            </strong>
                          </div>
                        )
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          </section>

          <section className="panel pipeline-panel">
            <div className="panel-heading">
              <div>
                <h3>Detection pipeline</h3>
                <p>
                  System components and integration status.
                </p>
              </div>

              <CheckCircle2
                size={21}
                className="pipeline-icon"
              />
            </div>

            <div className="pipeline-steps">
              <div className="pipeline-step complete">
                <span className="step-number">01</span>

                <div>
                  <strong>Audio input</strong>
                  <p>Upload interface ready</p>
                </div>

                <span className="step-status">READY</span>
              </div>

              <div
                className={`pipeline-step ${
                  result?.features?.mfcc_mean ? "complete" : ""
                }`}
              >
                <span className="step-number">02</span>

                <div>
                  <strong>Feature extraction</strong>
                  <p>
                    {result?.features?.mfcc_mean
                      ? "13 MFCC coefficients extracted"
                      : "Librosa MFCC extraction integrated"}
                  </p>
                </div>

                <span
                  className={`step-status ${
                    result?.features?.mfcc_mean ? "" : "pending"
                  }`}
                >
                  {result?.features?.mfcc_mean ? "READY" : "INTEGRATED"}
                </span>
              </div>

              <div className="pipeline-step">
                <span className="step-number">03</span>

                <div>
                  <strong>AI classification</strong>
                  <p>Trained model pending</p>
                </div>

                <span className="step-status pending">
                  PENDING
                </span>
              </div>

              <div className="pipeline-step">
                <span className="step-number">04</span>

                <div>
                  <strong>Threat assessment</strong>
                  <p>Classifier and risk scoring pending</p>
                </div>

                <span className="step-status pending">
                  PENDING
                </span>
              </div>
            </div>
          </section>

          <footer className="page-footer">
            <span>
              <ShieldCheck size={15} />
              VoiceShield · AI Safety &amp; Cybersecurity
            </span>

            <span>
              Research prototype · Not for production security decisions
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}
