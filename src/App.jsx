
import { useRef, useState } from "react";
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
  LockKeyhole,
  ArrowUpRight,
  Radio,
} from "lucide-react";

import "./App.css";

export default function App() {
  const inputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [dragging, setDragging] = useState(false);
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

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);
    handleFile(event.dataTransfer.files?.[0]);
  }

  async function analyzeAudio() {
    if (!file) {
      setMessage("Please upload an audio file first.");
      return;
    }

    setAnalyzing(true);
    setResult(null);
    setMessage("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Audio analysis failed."
        );
      }

      setResult(data);

      setMessage(
        data.classification === "spoof"
          ? "Potential synthetic voice detected."
          : "This recording was classified as bonafide."
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

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  const isSpoof = result?.classification === "spoof";
  const risk = Number(result?.risk_score ?? 0);
  const confidence = Number(result?.confidence ?? 0);

  return (
    <div className="app-shell">

      {/* SIDEBAR */}

      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
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
          >
            <X size={20} />
          </button>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>
          <a className="nav-item active" href="#dashboard">
            <LayoutDashboard size={19} />
            Dashboard
          </a>

          <a className="nav-item" href="#analysis">
            <AudioLines size={19} />
            Audio Analysis
          </a>

          <a className="nav-item" href="#history">
            <History size={19} />
            Scan History
          </a>

          <a className="nav-item" href="#settings">
            <Settings size={19} />
            Settings
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot" />

            <div>
              <strong>System online</strong>
              <p>ML model integrated</p>
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
          onClick={() => setMobileMenu(false)}
          aria-label="Close navigation"
        />
      )}

      {/* MAIN AREA */}

      <main className="main-area" id="dashboard">

        {/* TOPBAR */}

        <header className="topbar">
          <button
            className="menu-button"
            onClick={() => setMobileMenu(true)}
          >
            <Menu size={22} />
          </button>

          <div className="breadcrumb">
            Workspace <span>/</span> <strong>Dashboard</strong>
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

          {/* PAGE INTRO */}

          <section className="welcome">
            <div>
              <div className="eyebrow">
                <Activity size={15} />
                VOICE AUTHENTICITY INTELLIGENCE
              </div>

              <h1>
                Voice Threat <span>Detection</span>
              </h1>

              <p>
                Detect synthetic speech and investigate potential
                voice-cloning impersonation attacks.
              </p>
            </div>

            <div className="secure-badge">
              <LockKeyhole size={17} />
              Secure analysis workspace
            </div>
          </section>

          {/* OVERVIEW CARDS */}

          <section className="stats-grid">

            <div className="stat-card">
              <div className="stat-top">
                <span>Detection engine</span>
                <Radio size={19} />
              </div>

              <div className="stat-value stat-engine">
                ONLINE
              </div>

              <p>Logistic Regression · MFCC</p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Current analysis</span>
                <FileAudio size={19} />
              </div>

              <div className="stat-value stat-file">
                {file ? "1 FILE" : "—"}
              </div>

              <p>
                {file ? file.name : "No recording selected"}
              </p>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Threat assessment</span>
                <AlertTriangle size={19} />
              </div>

              <div className="stat-value">
                {result ? (isSpoof ? "ALERT" : "CLEAR") : "—"}
              </div>

              <p>
                {result
                  ? isSpoof
                    ? "Potential spoof detected"
                    : "Classified as bonafide"
                  : "Awaiting audio analysis"}
              </p>
            </div>

          </section>

          {/* UPLOAD SECTION */}

          <section className="panel upload-panel" id="analysis">
            <div className="section-heading">
              <div>
                <div className="section-kicker">STEP 01</div>
                <h2>Upload audio recording</h2>
                <p>
                  Select a recording to begin synthetic voice detection.
                </p>
              </div>

              <div className="section-icon">
                <Upload size={23} />
              </div>
            </div>

            <div
              className={`dropzone ${dragging ? "dragging" : ""}`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  inputRef.current?.click();
                }
              }}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".wav,.flac,.ogg,audio/wav,audio/flac,audio/ogg"
                onChange={(event) =>
                  handleFile(event.target.files?.[0])
                }
                hidden
              />

              <div className="upload-icon">
                <Upload size={28} />
              </div>

              <h3>
                {dragging
                  ? "Drop your audio here"
                  : "Drag and drop your audio"}
              </h3>

              <p>
                Or <span>browse files</span> from your computer
              </p>

              <div className="file-formats">
                WAV <span>•</span> FLAC <span>•</span> OGG
              </div>
            </div>

            {file && (
              <div className="selected-file">
                <div className="file-icon">
                  <FileAudio size={23} />
                </div>

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

            <div className="upload-actions">
              <button
                className="analyze-button"
                onClick={analyzeAudio}
                disabled={analyzing || !file}
              >
                <ShieldCheck size={20} />

                {analyzing
                  ? "Analyzing recording..."
                  : "Analyze recording"}

                {!analyzing && <ArrowUpRight size={19} />}
              </button>

              <span className="upload-hint">
                Maximum file size: 20 MB
              </span>
            </div>

            {message && (
              <div className={`feedback ${result ? "success" : ""}`}>
                {result && <CheckCircle2 size={18} />}
                {!result && <AlertTriangle size={18} />}
                {message}
              </div>
            )}

            <div className="privacy-note">
              <LockKeyhole size={15} />
              Audio is processed through the VoiceShield backend
              using an MFCC-based machine learning model.
            </div>
          </section>

          {/* RESULTS */}

          <section className="results-section">
            <div className="results-title">
              <div>
                <div className="section-kicker">STEP 02</div>
                <h2>Detection report</h2>
                <p>Classification and audio threat assessment.</p>
              </div>

              <span className={`report-status ${result ? "done" : ""}`}>
                <span />
                {result ? "ANALYSIS COMPLETE" : "AWAITING ANALYSIS"}
              </span>
            </div>

            {!result ? (
              <div className="empty-report">
                <div className="empty-report-icon">
                  <ShieldCheck size={40} />
                </div>

                <h3>Waiting for audio analysis</h3>

                <p>
                  Upload a voice recording above and click Analyze
                  recording. Your detection report will appear here.
                </p>
              </div>
            ) : (
              <>
                {/* LARGE CLASSIFICATION RESULT */}

                <div className={`verdict-card ${isSpoof ? "spoof" : "bonafide"}`}>
                  <div className="verdict-main">
                    <div className="verdict-icon">
                      {isSpoof ? (
                        <AlertTriangle size={32} />
                      ) : (
                        <ShieldCheck size={32} />
                      )}
                    </div>

                    <div>
                      <span className="verdict-label">
                        VOICE CLASSIFICATION
                      </span>

                      <h2>
                        {isSpoof ? "POTENTIAL SPOOF" : "BONAFIDE"}
                      </h2>

                      <p>
                        {isSpoof
                          ? "The model identified characteristics associated with synthetic speech."
                          : "The model classified this recording as genuine speech."}
                      </p>
                    </div>
                  </div>

                  <div className="verdict-tag">
                    {isSpoof ? "THREAT DETECTED" : "NO THREAT DETECTED"}
                  </div>
                </div>

                {/* LARGE SCORE CARDS */}

                <div className="result-metrics">

                  <div className="metric-card risk-card">
                    <div className="metric-heading">
                      <span> SPOOF RISK SCORE </span>
                      <AlertTriangle size={19} />
                    </div>

                    <div className="metric-number">
                      {risk.toFixed(2)}
                      <small>%</small>
                    </div>

                    <div className="risk-track">
                      <div
                        className={`risk-fill ${isSpoof ? "high" : "low"}`}
                        style={{
                          width: `${Math.min(100, Math.max(0, risk))}%`,
                        }}
                      />
                    </div>

                    <p>
                      {risk >= 70
                        ? "High model-estimated spoof probability"
                        : risk >= 40
                          ? "Moderate model-estimated spoof probability"
                          : "Low model-estimated spoof probability"}
                    </p>
                  </div>

                  <div className="metric-card confidence-card">
                    <div className="metric-heading">
                      <span> MODEL SCORE </span>
                      <Activity size={19} />
                    </div>

                    <div className="metric-number">
                      {confidence.toFixed(2)}
                      <small>%</small>
                    </div>

                    <p>
                      Maximum predicted class probability.
                      This score is not a guarantee of correctness.
                    </p>
                  </div>

                </div>

                {/* AUDIO DETAILS */}

                <div className="panel details-panel">
                  <div className="section-heading">
                    <div>
                      <div className="section-kicker">RECORDING INFORMATION</div>
                      <h2>Audio properties</h2>
                    </div>

                    <div className="section-icon">
                      <AudioLines size={22} />
                    </div>
                  </div>

                  <div className="audio-details-grid">
                    <div className="audio-detail">
                      <span>FILE NAME</span>
                      <strong>{file?.name ?? "—"}</strong>
                    </div>

                    <div className="audio-detail">
                      <span>DURATION</span>
                      <strong>
                        {result.duration_seconds} seconds
                      </strong>
                    </div>

                    <div className="audio-detail">
                      <span>SAMPLE RATE</span>
                      <strong>{result.sample_rate} Hz</strong>
                    </div>

                    <div className="audio-detail">
                      <span>CHANNELS</span>
                      <strong>{result.channels}</strong>
                    </div>

                    <div className="audio-detail">
                      <span>DETECTION MODEL</span>
                      <strong>{result.detection_model}</strong>
                    </div>

                    <div className="audio-detail">
                      <span>FEATURE EXTRACTION</span>
                      <strong>
                        {result.features?.mfcc_coefficients ?? 13} MFCCs
                      </strong>
                    </div>
                  </div>
                </div>

                {/* MFCC FEATURES */}

                {result.features?.mfcc_mean && (
                  <div className="panel features-panel">
                    <div className="section-heading">
                      <div>
                        <div className="section-kicker">SIGNAL ANALYSIS</div>
                        <h2>MFCC feature values</h2>
                        <p>
                          Extracted mean coefficients from the recording.
                        </p>
                      </div>
                    </div>

                    <div className="mfcc-grid">
                      {result.features.mfcc_mean.map((value, index) => (
                        <div className="mfcc-item" key={index}>
                          <span>MFCC {index + 1}</span>
                          <strong>{Number(value).toFixed(3)}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </section>

          {/* PIPELINE */}

          <section className="panel pipeline-panel">
            <div className="section-heading">
              <div>
                <div className="section-kicker">SYSTEM OVERVIEW</div>
                <h2>Detection pipeline</h2>
                <p>VoiceShield processing stages.</p>
              </div>

              <div className="section-icon">
                <Activity size={22} />
              </div>
            </div>

            <div className="pipeline-steps">
              {[
                ["01", "Audio input", "Recording uploaded"],
                ["02", "Feature extraction", "Librosa · 13 MFCC coefficients"],
                ["03", "AI classification", "Logistic Regression model"],
                ["04", "Threat assessment", "Classification and risk scoring"],
              ].map(([number, title, description]) => (
                <div className="pipeline-step" key={number}>
                  <span className="step-number">{number}</span>

                  <div>
                    <strong>{title}</strong>
                    <p>{description}</p>
                  </div>

                  <span className="step-status">INTEGRATED</span>
                </div>
              ))}
            </div>
          </section>

          {/* FOOTER */}

          <footer className="page-footer">
            <span>
              <ShieldCheck size={16} />
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
