import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const ProfileManagement: React.FC = () => {
  const { session, signIn, isPending } = useAuth();
  const [profileData, setProfileData] = useState({
    developerLevel: '',
    roboticsInterests: '',
    preferredAiModel: '',
    learningGoals: '',
    programmingLanguages: '',
    yearsExperience: 0
  });
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  // Load profile data when session is available
  useEffect(() => {
    if (session?.user) {
      setProfileData({
        developerLevel: session.user.developerLevel || '',
        roboticsInterests: session.user.roboticsInterests || '',
        preferredAiModel: session.user.preferredAiModel || '',
        learningGoals: session.user.learningGoals || '',
        programmingLanguages: session.user.programmingLanguages || '',
        yearsExperience: session.user.yearsExperience || 0
      });
    }
  }, [session]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: name === 'yearsExperience' ? parseInt(value, 10) : value
    }));
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // In a real implementation, we would call an API to update the profile
      // This is just a frontend placeholder
      console.log('Saving profile:', profileData);
      
      // Show success message
      alert('Profile updated successfully!');
      setIsEditing(false);
    } catch (err) {
      console.error('Error updating profile:', err);
      alert('Error updating profile');
    } finally {
      setLoading(false);
    }
  };

  if (!session) {
    return (
      <div className="p-6">
        <p>Please sign in to view your profile.</p>
        <button 
          onClick={() => signIn?.email({ email: '', password: '', callbackURL: '/profile' })}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Sign In
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Profile Settings</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">User Information</h2>
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Edit Profile
            </button>
          ) : (
            <div className="space-x-2">
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveProfile}
                disabled={loading}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Email</label>
            <p className="p-2 bg-gray-100 rounded">{session.user.email}</p>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Full Name</label>
            <p className="p-2 bg-gray-100 rounded">{session.user.firstName} {session.user.lastName}</p>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Developer Level</label>
            {isEditing ? (
              <select
                name="developerLevel"
                value={profileData.developerLevel}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
              >
                <option value="">Select level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            ) : (
              <p className="p-2 bg-gray-100 rounded">{profileData.developerLevel || 'Not specified'}</p>
            )}
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Years of Experience</label>
            {isEditing ? (
              <input
                type="number"
                name="yearsExperience"
                value={profileData.yearsExperience}
                onChange={handleInputChange}
                min="0"
                max="50"
                className="w-full p-2 border rounded"
              />
            ) : (
              <p className="p-2 bg-gray-100 rounded">{profileData.yearsExperience || 0} years</p>
            )}
          </div>
          
          <div className="md:col-span-2 mb-4">
            <label className="block text-sm font-medium mb-1">Programming Languages</label>
            {isEditing ? (
              <input
                type="text"
                name="programmingLanguages"
                value={profileData.programmingLanguages}
                onChange={handleInputChange}
                placeholder="Comma-separated: Python, JavaScript, C++"
                className="w-full p-2 border rounded"
              />
            ) : (
              <p className="p-2 bg-gray-100 rounded">{profileData.programmingLanguages || 'Not specified'}</p>
            )}
          </div>
          
          <div className="md:col-span-2 mb-4">
            <label className="block text-sm font-medium mb-1">Robotics Interests</label>
            {isEditing ? (
              <textarea
                name="roboticsInterests"
                value={profileData.roboticsInterests}
                onChange={handleInputChange}
                placeholder="What aspects of robotics interest you most?"
                rows={3}
                className="w-full p-2 border rounded"
              />
            ) : (
              <p className="p-2 bg-gray-100 rounded">{profileData.roboticsInterests || 'Not specified'}</p>
            )}
          </div>
          
          <div className="md:col-span-2 mb-4">
            <label className="block text-sm font-medium mb-1">Learning Goals</label>
            {isEditing ? (
              <textarea
                name="learningGoals"
                value={profileData.learningGoals}
                onChange={handleInputChange}
                placeholder="What do you hope to achieve?"
                rows={3}
                className="w-full p-2 border rounded"
              />
            ) : (
              <p className="p-2 bg-gray-100 rounded">{profileData.learningGoals || 'Not specified'}</p>
            )}
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Preferred AI Model</label>
            {isEditing ? (
              <select
                name="preferredAiModel"
                value={profileData.preferredAiModel}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
              >
                <option value="">Select model</option>
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
                <option value="chatkit">ChatKit</option>
              </select>
            ) : (
              <p className="p-2 bg-gray-100 rounded">{profileData.preferredAiModel || 'Not specified'}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileManagement;