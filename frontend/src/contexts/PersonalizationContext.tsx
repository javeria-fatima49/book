import React, { createContext, useContext, useReducer, useEffect } from 'react';

interface PersonalizationSettings {
  difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
  preferredModel: 'openai' | 'gemini' | 'chatkit';
  theme: 'light' | 'dark' | 'auto';
  learningPace: 'slow' | 'medium' | 'fast';
  codeExamplesLevel: 'simplified' | 'detailed' | 'expert';
  contentDepth: 'overview' | 'comprehensive' | 'deep-dive';
  showVisualAids: boolean;
  preferredLanguage: string;
  preferredNotation: 'pseudocode' | 'typescript' | 'python';
}

interface PersonalizationState {
  settings: PersonalizationSettings;
  isInitialized: boolean;
}

interface PersonalizationContextType extends PersonalizationState {
  updateSettings: (newSettings: Partial<PersonalizationSettings>) => void;
  resetSettings: () => void;
}

// Default settings
const DEFAULT_SETTINGS: PersonalizationSettings = {
  difficultyLevel: 'intermediate',
  preferredModel: 'openai',
  theme: 'auto',
  learningPace: 'medium',
  codeExamplesLevel: 'detailed',
  contentDepth: 'comprehensive',
  showVisualAids: true,
  preferredLanguage: 'en',
  preferredNotation: 'typescript'
};

// Action types
type PersonalizationAction =
  | { type: 'UPDATE_SETTINGS'; payload: Partial<PersonalizationSettings> }
  | { type: 'RESET_SETTINGS' }
  | { type: 'LOAD_FROM_STORAGE'; payload: PersonalizationSettings }
  | { type: 'INITIALIZED' };

const initialState: PersonalizationState = {
  settings: DEFAULT_SETTINGS,
  isInitialized: false
};

const personalizationReducer = (
  state: PersonalizationState,
  action: PersonalizationAction
): PersonalizationState => {
  switch (action.type) {
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      };
    case 'RESET_SETTINGS':
      return {
        ...state,
        settings: DEFAULT_SETTINGS
      };
    case 'LOAD_FROM_STORAGE':
      return {
        ...state,
        settings: { ...DEFAULT_SETTINGS, ...action.payload },
        isInitialized: true
      };
    case 'INITIALIZED':
      return {
        ...state,
        isInitialized: true
      };
    default:
      return state;
  }
};

const PersonalizationContext = createContext<PersonalizationContextType | undefined>(undefined);

export const PersonalizationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(personalizationReducer, initialState);

  // Load settings from localStorage on initial render
  useEffect(() => {
    const savedSettings = localStorage.getItem('personalizationSettings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        dispatch({ type: 'LOAD_FROM_STORAGE', payload: parsedSettings });
      } catch (error) {
        console.error('Failed to load personalization settings:', error);
        dispatch({ type: 'LOAD_FROM_STORAGE', payload: DEFAULT_SETTINGS });
      }
    } else {
      dispatch({ type: 'LOAD_FROM_STORAGE', payload: DEFAULT_SETTINGS });
    }
  }, []);

  const updateSettings = (newSettings: Partial<PersonalizationSettings>) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: newSettings });
    
    // Save to localStorage
    const updatedSettings = { ...state.settings, ...newSettings };
    localStorage.setItem('personalizationSettings', JSON.stringify(updatedSettings));
  };

  const resetSettings = () => {
    dispatch({ type: 'RESET_SETTINGS' });
    localStorage.setItem('personalizationSettings', JSON.stringify(DEFAULT_SETTINGS));
  };

  return (
    <PersonalizationContext.Provider
      value={{
        ...state,
        updateSettings,
        resetSettings
      }}
    >
      {children}
    </PersonalizationContext.Provider>
  );
};

export const usePersonalization = (): PersonalizationContextType => {
  const context = useContext(PersonalizationContext);
  if (!context) {
    throw new Error('usePersonalization must be used within a PersonalizationProvider');
  }
  return context;
};