import React, { useState } from 'react';
import { queryAgent } from '../services/agent_api_client';

/**
 * Props for the AgentSkills component.
 */
interface AgentSkillsProps {
  /** The base URL for the backend API. */
  backendApiUrl: string;
}

/**
 * A React functional component that provides access to various agent skills
 * such as summarization, quiz generation, and semantic search.
 *
 * @param {AgentSkillsProps} { backendApiUrl } - The props for the component, including the backend API URL.
 */
const AgentSkills: React.FC<AgentSkillsProps> = ({ backendApiUrl }) => {
  /** @type {string} skillType - State to store the selected skill type. */
  const [skillType, setSkillType] = useState<'summary' | 'quiz' | 'search'>('summary');
  /** @type {string} inputText - State to store the input text for the skill. */
  const [inputText, setInputText] = useState<string>('');
  /** @type {any} result - State to store the result from the skill execution. */
  const [result, setResult] = useState<any>(null);
  /** @type {boolean} loading - State to indicate if a skill is currently being executed. */
  const [loading, setLoading] = useState<boolean>(false);
  /** @type {string | null} error - State to store any error message. */
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles the execution of the selected agent skill.
   */
  const handleExecuteSkill = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Prepare the request based on the selected skill
      let requestData = {};
      if (skillType === 'summary') {
        requestData = {
          skills: ['summary'],
          input_data: {
            text: inputText,
            max_length: 150,
            min_length: 50
          }
        };
      } else if (skillType === 'quiz') {
        requestData = {
          skills: ['quiz'],
          input_data: {
            action: 'generate',
            content: inputText,
            num_questions: 5
          }
        };
      } else if (skillType === 'search') {
        requestData = {
          skills: ['search'],
          input_data: {
            query: inputText,
            limit: 5
          }
        };
      }

      // Call the agent orchestration API
      const response = await queryAgent(requestData, backendApiUrl);
      setResult(response.results[0].result.data);
    } catch (err: any) {
      console.error('Error executing agent skill:', err);
      setError(err.message || 'Failed to execute agent skill.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="agent-skills-container">
      <h3>AI Agent Skills</h3>
      
      <div className="skill-selector">
        <label>Select Skill: </label>
        <select
          value={skillType}
          onChange={(e) => setSkillType(e.target.value as any)}
        >
          <option value="summary">Summary</option>
          <option value="quiz">Quiz Generator</option>
          <option value="search">Semantic Search</option>
        </select>
      </div>
      
      <div className="input-area">
        <label>
          {skillType === 'summary' ? 'Text to summarize:' :
           skillType === 'quiz' ? 'Content for quiz:' :
           'Search query:'}
        </label>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={
            skillType === 'summary' ? 'Enter text to summarize...' :
            skillType === 'quiz' ? 'Enter content to generate quiz from...' :
            'Enter search query...'
          }
          rows={5}
          cols={50}
        />
      </div>
      
      <button onClick={handleExecuteSkill} disabled={loading}>
        {loading ? 'Processing...' : `Execute ${skillType.charAt(0).toUpperCase() + skillType.slice(1)} Skill`}
      </button>
      
      {error && (
        <div className="error-message" style={{ color: 'red', marginTop: '10px' }}>
          Error: {error}
        </div>
      )}
      
      {result && (
        <div className="result-area" style={{ marginTop: '20px', padding: '10px', border: '1px solid #ccc' }}>
          <h4>Result:</h4>
          {skillType === 'summary' && (
            <div>
              <p><strong>Summary:</strong> {result.summary}</p>
              <p><strong>Original Length:</strong> {result.original_length} characters</p>
              <p><strong>Summary Length:</strong> {result.summary_length} characters</p>
              <p><strong>Compression Ratio:</strong> {result.compression_ratio}</p>
            </div>
          )}
          
          {skillType === 'quiz' && (
            <div>
              <p><strong>Quiz ID:</strong> {result.id}</p>
              <p><strong>Total Questions:</strong> {result.total_questions}</p>
              <div>
                <h5>Questions:</h5>
                {result.questions.map((q: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #eee' }}>
                    <p><strong>Q{idx + 1}:</strong> {q.question}</p>
                    <ul>
                      {q.options.map((opt: string, optIdx: number) => (
                        <li key={optIdx}>{opt}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {skillType === 'search' && (
            <div>
              <p><strong>Query:</strong> {result.query}</p>
              <p><strong>Results Found:</strong> {result.count}</p>
              <div>
                <h5>Results:</h5>
                {result.results.slice(0, 3).map((r: any, idx: number) => (
                  <div key={idx} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #eee' }}>
                    <p><strong>Score:</strong> {r.score}</p>
                    <p>{r.text.substring(0, 200)}...</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentSkills;