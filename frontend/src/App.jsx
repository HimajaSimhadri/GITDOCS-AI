import { useState } from "react";
import "./App.css";

const BACKEND_URL = "https://https://gitdocs-ai-gyzx.onrender.com";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");
  const [indexStatus, setIndexStatus] = useState("");

  const [loadingIndex, setLoadingIndex] = useState(false);
  const [loadingAnswer, setLoadingAnswer] = useState(false);

  const [sources, setSources] = useState(0);
  const [chunks, setChunks] = useState(0);

  // ============================
  // INDEX REPOSITORY
  // ============================

  const indexRepository = async () => {
    if (!repoUrl.trim()) {
      setIndexStatus("Please enter a GitHub repository URL.");
      return;
    }

    setLoadingIndex(true);
    setIndexStatus("Searching your repository...");
    setAnswer("");

    try {
      const response = await fetch(`${BACKEND_URL}/index`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: repoUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || "Failed to index repository");
      }

      setSources(data.files || 0);
      setChunks(data.chunks || 0);

      setIndexStatus(
        `Repository indexed successfully! ${data.files || 0} files and ${
          data.chunks || 0
        } chunks added.`
      );
    } catch (error) {
      console.error(error);

      setIndexStatus(
        "Could not connect to GitDocs AI backend."
      );
    } finally {
      setLoadingIndex(false);
    }
  };

  // ============================
  // ASK QUESTION
  // ============================

  const askQuestion = async (customQuestion = null) => {
    const finalQuestion =
      customQuestion !== null ? customQuestion : question;

    if (!finalQuestion.trim()) {
      return;
    }

    setQuestion(finalQuestion);
    setLoadingAnswer(true);
    setAnswer("");

    try {
      const response = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: finalQuestion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      setAnswer(data.answer || "No answer received.");
    } catch (error) {
      console.error(error);

      setAnswer(
        "❌ Could not connect to GitDocs AI backend."
      );
    } finally {
      setLoadingAnswer(false);
    }
  };

  // ============================
  // ENTER KEY
  // ============================

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      askQuestion();
    }
  };

  // ============================
  // QUICK QUESTIONS
  // ============================

  const quickQuestions = [
    {
      icon: "▱",
      text: "What frontend technology is being used?",
    },
    {
      icon: "▤",
      text: "What backend technology is being used?",
    },
    {
      icon: "◉",
      text: "What database is being used?",
    },
    {
      icon: "▣",
      text: "Summarize the architecture",
    },
  ];

  return (
    <div className="app">

      {/* =================================
          HEADER
      ================================= */}

      <header className="navbar">

        <div className="brand">
          <div className="brand-icon">ϟ</div>

          <div>
            <div className="brand-name">
              GitDocs <span>AI</span>
            </div>

            <div className="brand-subtitle">
              Repository assistant
            </div>
          </div>
        </div>

        <div className="ai-status">
          <span className="status-dot"></span>
          AI ready · RAG + Gemini
        </div>

      </header>


      {/* =================================
          MAIN TWO COLUMN LAYOUT
      ================================= */}

      <main className="main-layout">

        {/* =================================
            LEFT PANEL
        ================================= */}

        <section className="repository-panel">

          <div className="panel-content">

            <h2>
              <span className="orange-icon">⌘</span>
              Connect GitHub repository
            </h2>

            <p className="panel-description">
              Point GitDocs AI at a repo. It indexes code,
              docs and structure so answers stay grounded
              in real sources.
            </p>


            {/* Repository URL */}

            <input
              className="repo-input"
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
            />


            {/* Index button */}

            <button
              className="index-button"
              onClick={indexRepository}
              disabled={loadingIndex}
            >
              {loadingIndex
                ? "Indexing..."
                : "Index repository"}
            </button>


            {/* Status */}

            {indexStatus && (
              <div
                className={`index-status ${
                  indexStatus.includes("successfully")
                    ? "success"
                    : indexStatus.includes("Searching")
                    ? "searching"
                    : "error"
                }`}
              >
                <span className="status-small-dot"></span>
                {indexStatus}
              </div>
            )}

          </div>


          {/* =================================
              STATS
          ================================= */}

          <div className="stats">

            <div className="stat">
              <div className="stat-number">
                {sources}
              </div>

              <div className="stat-label">
                Sources
              </div>
            </div>


            <div className="stat">
              <div className="stat-number">
                {chunks}
              </div>

              <div className="stat-label">
                Chunks
              </div>
            </div>


            <div className="stat">
              <div className="stat-number gemini">
                Gemini
              </div>

              <div className="stat-label">
                Model
              </div>
            </div>

          </div>

        </section>


        {/* =================================
            RIGHT CHAT PANEL
        ================================= */}

        <section className="chat-panel">

          <div className="chat-header">

            <h1>
              Ask GitDocs AI anything
            </h1>

            <p>
              Ask a question about your indexed repository —
              architecture, dependencies, conventions or a
              single function.
            </p>

          </div>


          {/* =================================
              QUICK QUESTIONS
          ================================= */}

          <div className="question-grid">

            {quickQuestions.map((item, index) => (

              <button
                key={index}
                className="question-card"
                onClick={() => askQuestion(item.text)}
              >

                <span className="question-icon">
                  {item.icon}
                </span>

                <span>
                  {item.text}
                </span>

              </button>

            ))}

          </div>


          {/* =================================
              ANSWER AREA
          ================================= */}

          <div className="answer-area">

            {loadingAnswer && (
              <div className="loading-answer">
                <span className="loading-dot"></span>
                Searching your repository...
              </div>
            )}

            {!loadingAnswer && answer && (

              <div className="answer-container">

                <div className="answer-title">
                  🤖 GitDocs AI
                </div>

                <div className="answer-text">
                  {answer}
                </div>

              </div>

            )}

          </div>


          {/* =================================
              QUESTION INPUT
          ================================= */}

          <div className="chat-input-wrapper">

            <input
              className="chat-input"
              type="text"
              value={question}
              onChange={(e) =>
                setQuestion(e.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask something about your repository..."
            />

            <button
              className="send-button"
              onClick={() => askQuestion()}
              disabled={loadingAnswer}
            >
              ↑
            </button>

          </div>

        </section>

      </main>


      {/* =================================
          FOOTER
      ================================= */}

      <footer className="footer">
        <span>ϟ</span>
        GitDocs AI · Powered by RAG + Gemini
      </footer>

    </div>
  );
}

export default App;