import React, { useState } from 'react';
import { usePersonalization } from '../contexts/PersonalizationContext';

const PersonalizationPanel: React.FC = () => {
  const { settings, updateSettings } = usePersonalization();
  const [isOpen, setIsOpen] = useState(false);
  const [tempSettings, setTempSettings] = useState(settings);

  const handleSave = () => {
    updateSettings(tempSettings);
    setIsOpen(false);
  };

  const handleReset = () => {
    const defaultSettings = {
      difficultyLevel: 'intermediate' as const,
      preferredModel: 'openai' as const,
      theme: 'auto' as const,
      learningPace: 'medium' as const,
      codeExamplesLevel: 'detailed' as const,
      contentDepth: 'comprehensive' as const,
      showVisualAids: true,
      preferredLanguage: 'en',
      preferredNotation: 'typescript' as const
    };
    setTempSettings(defaultSettings);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-500 text-white p-3 rounded-full shadow-lg z-50 hover:bg-blue-600 transition-colors"
        aria-label="Personalization Settings"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Personalization Settings</h2>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                {/* Difficulty Level */}
                <div>
                  <label className="block text-sm font-medium mb-2">Difficulty Level</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['beginner', 'intermediate', 'advanced'] as const).map(level => (
                      <button
                        key={level}
                        type="button"
                        onClick={() => setTempSettings({...tempSettings, difficultyLevel: level})}
                        className={`py-2 px-3 rounded border ${
                          tempSettings.difficultyLevel === level
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700'
                        }`}
                      >
                        {level.charAt(0).toUpperCase() + level.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Learning Pace */}
                <div>
                  <label className="block text-sm font-medium mb-2">Learning Pace</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['slow', 'medium', 'fast'] as const).map(pace => (
                      <button
                        key={pace}
                        type="button"
                        onClick={() => setTempSettings({...tempSettings, learningPace: pace})}
                        className={`py-2 px-3 rounded border ${
                          tempSettings.learningPace === pace
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700'
                        }`}
                      >
                        {pace.charAt(0).toUpperCase() + pace.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Content Depth */}
                <div>
                  <label className="block text-sm font-medium mb-2">Content Depth</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['overview', 'comprehensive', 'deep-dive'] as const).map(depth => (
                      <button
                        key={depth}
                        type="button"
                        onClick={() => setTempSettings({...tempSettings, contentDepth: depth})}
                        className={`py-2 px-3 rounded border ${
                          tempSettings.contentDepth === depth
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700'
                        }`}
                      >
                        {depth.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Code Examples Level */}
                <div>
                  <label className="block text-sm font-medium mb-2">Code Examples Level</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['simplified', 'detailed', 'expert'] as const).map(level => (
                      <button
                        key={level}
                        type="button"
                        onClick={() => setTempSettings({...tempSettings, codeExamplesLevel: level})}
                        className={`py-2 px-3 rounded border ${
                          tempSettings.codeExamplesLevel === level
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700'
                        }`}
                      >
                        {level.charAt(0).toUpperCase() + level.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Preferred Notation */}
                <div>
                  <label className="block text-sm font-medium mb-2">Preferred Code Notation</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['pseudocode', 'typescript', 'python'] as const).map(notation => (
                      <button
                        key={notation}
                        type="button"
                        onClick={() => setTempSettings({...tempSettings, preferredNotation: notation})}
                        className={`py-2 px-3 rounded border ${
                          tempSettings.preferredNotation === notation
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700'
                        }`}
                      >
                        {notation}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Preferred AI Model */}
                <div>
                  <label className="block text-sm font-medium mb-2">Preferred AI Model</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['openai', 'gemini', 'chatkit'] as const).map(model => (
                      <button
                        key={model}
                        type="button"
                        onClick={() => setTempSettings({...tempSettings, preferredModel: model})}
                        className={`py-2 px-3 rounded border ${
                          tempSettings.preferredModel === model
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700'
                        }`}
                      >
                        {model.charAt(0).toUpperCase() + model.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Visual Aids Toggle */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="showVisualAids"
                    checked={tempSettings.showVisualAids}
                    onChange={(e) => setTempSettings({...tempSettings, showVisualAids: e.target.checked})}
                    className="mr-2"
                  />
                  <label htmlFor="showVisualAids" className="text-sm font-medium">
                    Show Visual Aids
                  </label>
                </div>
              </div>

              <div className="mt-6 flex justify-between">
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
                >
                  Reset to Default
                </button>
                <div className="space-x-2">
                  <button
                    type="button"
                    onClick={() => setIsOpen(false)}
                    className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSave}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Save Settings
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PersonalizationPanel;