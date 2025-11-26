"use client";

import { useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";

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
  const [loading, setLoading] = useState(false);

  const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL;

  async function runCode() {
    setLoading(true);
    setOutput("");
    setError("");
    setMentor(null);

    try {
      // 1. Send code to backend /run
      const runRes = await axios.post(`${BACKEND}/run`, { code });
      const stdout = runRes.data.stdout;
      const stderr = runRes.data.stderr;

      setOutput(stdout || "");
      setError(stderr || "");

      // 2. Send to mentor for explanation
      const mentorRes = await axios.post(`${BACKEND}/mentor/help`, {
        code,
        error: stderr || null,
        question: null
      });

      setMentor(mentorRes.data);

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
        bondo - scikit-learn mentor
      </header>

      <div className="flex flex-1 overflow-hidden">
        
        {/* Left side: Code editor */}
        <div className="w-1/2 h-full flex flex-col border-r">
          <div className="flex items-center justify-between p-2 border-b">
            <h2 className="text-lg font-medium">Code</h2>
            <button
              onClick={runCode}
              disabled={loading}
              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {loading ? "Running..." : "Run"}
            </button>
          </div>

          <Editor
            height="100%"
            defaultLanguage="python"
            value={code}
            onChange={(val) => setCode(val)}
            theme="vs-dark"
          />
        </div>

        {/* Right side */}
        <div className="w-1/2 h-full overflow-auto p-4 space-y-6">
          
          {/* Output */}
          <section>
            <h2 className="text-lg font-semibold">Output</h2>
            <pre className="bg-gray-100 p-3 rounded overflow-x-auto whitespace-pre-wrap">
              {output || "(no output)"}
            </pre>
          </section>

          {/* Error */}
          <section>
            <h2 className="text-lg font-semibold">Error</h2>
            <pre className="bg-red-100 p-3 rounded overflow-x-auto whitespace-pre-wrap">
              {error || "(no error)"}
            </pre>
          </section>

          {/* Mentor Panel */}
          <section>
            <h2 className="text-lg font-semibold">bondo's Guidance</h2>
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

                <div>
                  <h3 className="font-medium">Doc References</h3>
                  <ul className="space-y-2">
                    {mentor.doc_references?.map((ref) => (
                      <li
                        key={ref.id}
                        className="border p-2 rounded bg-gray-50"
                      >
                        <div className="font-semibold">{ref.title}</div>
                        <div className="text-sm text-gray-600 whitespace-pre-wrap">
                          {ref.text}
                        </div>
                        {ref.url && (
                          <a
                            href={ref.url}
                            target="_blank"
                            className="text-blue-600 text-sm"
                          >
                            {ref.url}
                          </a>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>

              </div>
            )}
          </section>

        </div>
      </div>
    </main>
  );
}