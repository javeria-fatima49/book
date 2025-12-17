import React from 'react';
import { usePersonalization } from '../contexts/PersonalizationContext';

interface PersonalizedContentProps {
  content: string;
  contentType?: 'text' | 'code' | 'explanation';
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
}

interface ChapterSection {
  id: string;
  title: string;
  content: string;
  codeExample?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  visualAid?: React.ReactNode;
  explanationLevel?: 'basic' | 'detailed' | 'advanced';
}

interface PersonalizedChapterContentProps {
  sections: ChapterSection[];
}

const PersonalizedContent: React.FC<PersonalizedContentProps> = ({ 
  content, 
  contentType = 'text',
  difficulty = 'intermediate'
}) => {
  const { settings } = usePersonalization();
  
  let adjustedContent = content;
  
  // Adjust complexity based on user's difficulty level
  if (settings.difficultyLevel === 'beginner') {
    // For beginners, simplify complex terminology
    adjustedContent = adjustedContent.replace(/\b(advanced|complex|sophisticated)\b/gi, 'fundamental');
    adjustedContent = adjustedContent.replace(/\b(expert|specialized)\b/gi, 'basic');
  } else if (settings.difficultyLevel === 'advanced') {
    // For advanced users, add more depth
    adjustedContent += '\n\n> **Advanced Note:** Consider performance implications and edge cases in production environments.';
  }
  
  // Adjust code examples based on selected level
  if (contentType === 'code') {
    if (settings.codeExamplesLevel === 'simplified') {
      // Remove complex configurations for simplified examples
      adjustedContent = adjustedContent.replace(/\/\/ Advanced configuration[\s\S]*?\n/g, '');
    } else if (settings.codeExamplesLevel === 'expert') {
      // Add expert-level comments and patterns
      adjustedContent += '\n// Production-ready implementation with error handling and optimization';
    }
  }
  
  return <div>{adjustedContent}</div>;
};

const PersonalizedChapterContent: React.FC<PersonalizedChapterContentProps> = ({ sections }) => {
  const { settings } = usePersonalization();

  // Filter sections based on user difficulty level
  const filteredSections = sections.filter(section => {
    const userLevel = settings.difficultyLevel;
    const sectionLevel = section.difficulty;
    
    // Map difficulty levels to numerical values
    const levelValues: Record<string, number> = {
      beginner: 1,
      intermediate: 2,
      advanced: 3
    };
    
    return levelValues[sectionLevel] <= levelValues[userLevel];
  });

  return (
    <div className="prose max-w-none dark:prose-invert">
      {filteredSections.map((section, index) => (
        <div key={section.id} className="mb-8">
          <h2 className="text-2xl font-bold mb-4">{section.title}</h2>
          
          <div className="mb-4">
            {/* Render adjusted content based on personalization */}
            <PersonalizedContent 
              content={section.content} 
              contentType="text"
              difficulty={section.difficulty}
            />
          </div>
          
          {/* Show visual aid if enabled and available */}
          {settings.showVisualAids && section.visualAid && (
            <div className="my-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              {section.visualAid}
            </div>
          )}
          
          {/* Show code example if available */}
          {section.codeExample && (
            <div className="my-4">
              <h3 className="font-semibold mb-2">Code Example:</h3>
              <PersonalizedContent 
                content={section.codeExample} 
                contentType="code"
                difficulty={section.difficulty}
              />
            </div>
          )}
          
          {/* Additional content based on personalization */}
          {settings.contentDepth === 'deep-dive' && section.explanationLevel === 'detailed' && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded">
              <h3 className="font-semibold mb-2">Deep Dive:</h3>
              <p>Additional in-depth analysis for advanced understanding...</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export { PersonalizedContent, PersonalizedChapterContent };