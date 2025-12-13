import { useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";
import DocsIframePanel from "../components/DocsIframePanel";

export default function Home() {
  const [code, setCode] = useState(`# Write your scikit-learn code here
from sklearn.linear_model import LinearRegression
import numpy as np

X = np.array([[1],[2],[3]])
y = np.array([2,4,6])

model = LinearRegression()
model.fit(X, y)
print("coef_", model.coef_)`);

  const [output, setOutput] = useState("");
  const [error, setError] = useState("");
  const [mentor, setMentor] = useState(null);
  const [activeDocUrl, setActiveDocUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL;
  
  function isIndexLikeUrl(url) {
    if (!url) return true;

    const lowered = url.toLowerCase();
    return (
      lowered.endsWith("/index.html") ||
      lowered.endsWith("/api.html") ||
      lowered.endsWith("/user_guide.html") ||
      lowered.includes("/api/index") ||
      lowered.includes("/modules/classes")
    );
  }

  function chooseBestDocUrl(docRefs) {
    if (!Array.isArray(docRefs)) return null;

    // 1. Strong preference: generated API reference pages
    const generated = docRefs.find(
      r => r.url && r.url.includes("/generated/")
    );
    if (generated) return generated.url;

    // 2. Non-index pages
    const nonIndex = docRefs.find(
      r => r.url && !isIndexLikeUrl(r.url)
    );
    if (nonIndex) return nonIndex.url;

    // 3. Fallback
    return docRefs.find(r => r.url)?.url || null;
  }

  async function runCode() {
    setLoading(true);
    setOutput("");
    setError("");
    setMentor(null);

    try {
      const runRes = await axios.post(`${BACKEND}/run`, { code });
      const stdout = runRes.data.stdout;
      const stderr = runRes.data.stderr;

      setOutput(stdout || "");
      setError(stderr || "");

      const mentorRes = await axios.post(`${BACKEND}/mentor/help`, {
        code,
        error: stderr || null,
        question: null,
      });

      setMentor(mentorRes.data);

      const docUrl = chooseBestDocUrl(mentorRes.data?.doc_references);
      setActiveDocUrl(docUrl);

      console.log(
        "Doc refs:",
        mentorRes.data?.doc_references?.map(r => r.url)
      );

    } catch (err) {
      console.error(err);
      setError("Frontend error: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="h-screen flex flex-col">
      <header className="p-4 bg-gray-900 text-white text-xl font-semibold">
        bondo — scikit-learn mentor
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Code editor */}
        <div className="w-1/3 h-full flex flex-col border-r">
          <div className="flex items-center justify-between p-2 border-b">
            <h2 className="text-lg font-medium">Code</h2>
            <button
              onClick={runCode}
              disabled={loading}
              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-60"
            >
              {loading ? "Running..." : "Run"}
            </button>
          </div>

          <Editor
            height="100%"
            defaultLanguage="python"
            value={code}
            onChange={(val) => setCode(val ?? "")}
            theme="vs-dark"
          />
        </div>

        {/* Output + mentor */}
        <div className="w-1/3 h-full overflow-auto p-4 space-y-6">
          <section>
            <h2 className="text-lg font-semibold">Output</h2>
            <pre className="bg-gray-100 p-3 rounded whitespace-pre-wrap">
              {output || "(no output)"}
            </pre>
          </section>

          <section>
            <h2 className="text-lg font-semibold">Error</h2>
            <pre className="bg-red-100 p-3 rounded whitespace-pre-wrap">
              {error || "(no error)"}
            </pre>
          </section>

          <section>
            <h2 className="text-lg font-semibold">bondo’s Guidance</h2>
            {!mentor && (
              <div className="text-gray-500">(Run code to get mentor feedback)</div>
            )}

            {mentor && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium">Explanation</h3>
                  <p className="bg-gray-50 p-3 rounded whitespace-pre-wrap">
                    {mentor.explanation}
                  </p>
                </div>

                <div>
                  <h3 className="font-medium">Suggested Fix</h3>
                  <pre className="bg-green-50 p-3 rounded whitespace-pre-wrap">
                    {mentor.suggested_fix}
                  </pre>
                </div>
              </div>
            )}
          </section>
        </div>

        {/* Docs iframe */}
        <div className="w-1/3 h-full">
          <DocsIframePanel docUrl={activeDocUrl} />
        </div>
      </div>
    </main>
  );
}
