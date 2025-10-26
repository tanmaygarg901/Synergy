'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import UserCard from '@/components/UserCard';
import { Loader2, Sparkles, Users } from 'lucide-react';

// Dynamically import Chatbot to avoid SSR issues
const Chatbot = dynamic(() => import('react-chatbot-kit').then(mod => mod.default), {
  ssr: false,
});

import config from '@/components/chatbot/config';
import MessageParser from '@/components/chatbot/MessageParser';
import ActionProvider from '@/components/chatbot/ActionProvider';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function Home() {
  const [appState, setAppState] = useState('chatting'); // 'chatting', 'loading', 'results'
  const [chatTranscript, setChatTranscript] = useState('');
  const [userProfile, setUserProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [sessionId] = useState(() => `session_${Date.now()}`);

  // Handle messages from chatbot
  const handleUserMessage = async (message, chatMessages) => {
    // Build chat transcript
    const transcript = chatMessages
      .map(msg => `${msg.type === 'bot' ? 'Assistant' : 'User'}: ${msg.message}`)
      .join('\n');
    
    setChatTranscript(transcript);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
        }),
      });

      const data = await response.json();
      
      // Check if trigger phrase was detected
      if (data.is_trigger) {
        // Transition to loading state
        setAppState('loading');
        
        // Find collaborators
        setTimeout(async () => {
          await findCollaborators(transcript + `\nUser: ${message}\nAssistant: ${data.response}`);
        }, 500);
      }

      return data.response;
    } catch (error) {
      console.error('Error sending message:', error);
      return "I'm having trouble connecting. Please try again.";
    }
  };

  const findCollaborators = async (fullTranscript) => {
    try {
      const response = await fetch(`${API_URL}/find-collaborators`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_transcript: fullTranscript,
          session_id: sessionId,
        }),
      });

      const data = await response.json();
      
      setUserProfile(data.your_profile);
      setMatches(data.matches);
      setAppState('results');
    } catch (error) {
      console.error('Error finding collaborators:', error);
      setAppState('chatting');
    }
  };

  const resetApp = () => {
    setAppState('chatting');
    setChatTranscript('');
    setUserProfile(null);
    setMatches([]);
  };

  // Custom ActionProvider that uses our handler
  const CustomActionProvider = class extends ActionProvider {
    constructor(createChatBotMessage, setStateFunc, createClientMessage, stateRef) {
      super(createChatBotMessage, setStateFunc);
      this.createClientMessage = createClientMessage;
      this.stateRef = stateRef;
    }

    handleUserMessage = async (message) => {
      const response = await handleUserMessage(message, this.stateRef.messages);
      
      const botMessage = this.createChatBotMessage(response);
      this.setState((prevState) => ({
        ...prevState,
        messages: [...prevState.messages, botMessage],
      }));
    };
  };

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Sparkles className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Synergy
            </h1>
          </div>
          <p className="text-muted-foreground">Find your perfect collaborator with AI</p>
        </div>

        {/* Chatting State */}
        {appState === 'chatting' && (
          <div className="max-w-4xl mx-auto">
            <Card className="shadow-xl">
              <CardContent className="p-6">
                <Chatbot
                  config={config}
                  messageParser={MessageParser}
                  actionProvider={CustomActionProvider}
                  placeholderText="Type your message..."
                  headerText="Chat with Synergy AI"
                />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Loading State */}
        {appState === 'loading' && (
          <div className="max-w-2xl mx-auto">
            <Card className="shadow-xl">
              <CardContent className="p-12 text-center">
                <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
                <h2 className="text-2xl font-semibold mb-2">Finding Your Perfect Match</h2>
                <p className="text-muted-foreground">
                  Analyzing your profile and searching our network...
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Results State */}
        {appState === 'results' && (
          <div className="max-w-6xl mx-auto space-y-8">
            {/* User Profile */}
            {userProfile && (
              <Card className="shadow-xl border-2 border-primary">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-6 h-6" />
                    Your Profile
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold text-lg mb-2">{userProfile.name}</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Looking for: {userProfile.looking_for}
                      </p>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <h4 className="text-sm font-semibold mb-2">Your Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {userProfile.skills?.map((skill, index) => (
                            <Badge key={index} variant="default">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold mb-2">Your Interests</h4>
                        <div className="flex flex-wrap gap-2">
                          {userProfile.interests?.map((interest, index) => (
                            <Badge key={index} variant="secondary">
                              {interest}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Matches */}
            <div>
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-primary" />
                Your Matches ({matches.length})
              </h2>
              
              {matches.length > 0 ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {matches.map((match, index) => (
                    <UserCard key={match.id || index} collaborator={match} />
                  ))}
                </div>
              ) : (
                <Card className="shadow-xl">
                  <CardContent className="p-12 text-center">
                    <p className="text-muted-foreground mb-4">
                      No matches found. Try adjusting your preferences.
                    </p>
                    <Button onClick={resetApp}>Start Over</Button>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Reset Button */}
            {matches.length > 0 && (
              <div className="text-center">
                <Button onClick={resetApp} variant="outline" size="lg">
                  Start New Search
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
