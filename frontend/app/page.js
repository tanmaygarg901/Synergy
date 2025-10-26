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
    <div className="min-h-screen w-full bg-[#f7f3ec] text-[#2f2a28]">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 lg:px-12">
        <header className="flex items-center justify-between text-sm font-medium text-[#2f2a28]">
          <span className="text-base font-semibold uppercase tracking-[0.2em]">Synergy</span>
          <nav className="flex gap-8 text-sm text-[#2f2a28]/85">
            <a href="#" className="transition-opacity hover:opacity-70">Features</a>
            <a href="#" className="transition-opacity hover:opacity-70">How it Works</a>
            <a href="#" className="transition-opacity hover:opacity-70">Community</a>
          </nav>
        </header>

        <main className="flex flex-1 flex-col">
          <section className="mt-24 flex flex-col items-center text-center">
            <h1 className="max-w-3xl text-5xl font-extrabold tracking-tight text-[#2f2a28] sm:text-6xl">
              Find Your Perfect Collaborator 🟧
            </h1>
            <p className="mt-6 max-w-2xl text-lg text-[#4f4a45]">
              A modern, AI-powered workspace that connects visionary builders with the right partners.
              Experience effortless collaboration in a clean, minimalist environment.
            </p>
            <div className="mt-12 flex justify-center">
              <button
                type="button"
                className="rounded-full bg-[#ff7a1a] px-14 py-6 text-lg font-semibold uppercase tracking-wide text-white shadow-[0_35px_60px_-25px_rgba(255,122,26,0.6)] transition-transform duration-300 hover:-translate-y-1 hover:shadow-[0_45px_80px_-35px_rgba(255,122,26,0.65)]"
              >
                Launch Synergy
              </button>
            </div>
            <div className="mt-6 flex flex-col items-center gap-3 text-sm text-[#6b7280]">
              <label className="inline-flex items-center gap-3">
                <input
                  type="checkbox"
                  readOnly
                  className="h-5 w-5 rounded-sm border border-[#d6d3ce] bg-transparent accent-[#ff7a1a]"
                />
                <span className="text-base font-medium">Curated collaborator matches</span>
              </label>
              <label className="inline-flex items-center gap-3">
                <input
                  type="checkbox"
                  readOnly
                  className="h-5 w-5 rounded-sm border border-[#d6d3ce] bg-transparent accent-[#ff7a1a]"
                />
                <span className="text-base font-medium">Personalized AI guidance</span>
              </label>
            </div>
          </section>

          <section className="mt-24 flex-1 pb-16">
            {/* Chatting State */}
            {appState === 'chatting' && (
              <div className="mx-auto max-w-4xl">
                <Card className="border border-[#efe6dc] bg-white/90 shadow-[0_25px_70px_-45px_rgba(15,15,15,0.6)]">
                  <CardContent className="p-6 md:p-8">
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
              <div className="mx-auto max-w-2xl">
                <Card className="border border-[#efe6dc] bg-white/90 shadow-[0_25px_70px_-45px_rgba(15,15,15,0.6)]">
                  <CardContent className="p-12 text-center">
                    <Loader2 className="mx-auto mb-6 h-12 w-12 animate-spin text-[#ff7a1a]" />
                    <h2 className="text-2xl font-semibold text-[#2f2a28]">Finding Your Perfect Match</h2>
                    <p className="mt-3 text-base text-[#6b6b6b]">
                      Analyzing your profile and exploring our network of innovators...
                    </p>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Results State */}
            {appState === 'results' && (
              <div className="mx-auto max-w-6xl space-y-10">
                {/* User Profile */}
                {userProfile && (
                  <Card className="border border-[#efe6dc] bg-white/95 shadow-[0_25px_70px_-45px_rgba(15,15,15,0.6)]">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-[#2f2a28]">
                        <Users className="h-6 w-6 text-[#2f2a28]" />
                        Your Profile
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-6 md:grid-cols-2">
                        <div>
                          <h3 className="text-lg font-semibold text-[#2f2a28]">{userProfile.name}</h3>
                          <p className="mt-2 text-sm text-[#7a746d]">
                            Looking for: {userProfile.looking_for}
                          </p>
                        </div>
                        <div className="space-y-3">
                          <div>
                            <h4 className="text-sm font-semibold text-[#2f2a28]">Your Skills</h4>
                            <div className="mt-2 flex flex-wrap gap-2">
                              {userProfile.skills?.map((skill, index) => (
                                <Badge key={index} variant="default">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-[#2f2a28]">Your Interests</h4>
                            <div className="mt-2 flex flex-wrap gap-2">
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
                  <h2 className="mb-6 flex items-center gap-2 text-2xl font-bold text-[#2f2a28]">
                    <Sparkles className="h-6 w-6 text-[#ff7a1a]" />
                    Your Matches ({matches.length})
                  </h2>

                  {matches.length > 0 ? (
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {matches.map((match, index) => (
                        <UserCard key={match.id || index} collaborator={match} />
                      ))}
                    </div>
                  ) : (
                    <Card className="border border-[#efe6dc] bg-white/90 shadow-[0_25px_70px_-45px_rgba(15,15,15,0.6)]">
                      <CardContent className="p-12 text-center">
                        <p className="mb-6 text-base text-[#7a746d]">
                          No matches found. Try adjusting your preferences.
                        </p>
                        <Button
                          onClick={resetApp}
                          className="rounded-full bg-[#ff7a1a] px-10 py-4 text-base font-semibold text-white shadow-[0_20px_45px_-25px_rgba(255,122,26,0.6)] hover:bg-[#ff7a1a]/90"
                        >
                          Start Over
                        </Button>
                      </CardContent>
                    </Card>
                  )}
                </div>

                {/* Reset Button */}
                {matches.length > 0 && (
                  <div className="text-center">
                    <Button
                      onClick={resetApp}
                      size="lg"
                      className="rounded-full bg-[#ff7a1a] px-10 py-4 text-base font-semibold text-white shadow-[0_20px_45px_-25px_rgba(255,122,26,0.6)] hover:bg-[#ff7a1a]/90"
                    >
                      Start New Search
                    </Button>
                  </div>
                )}
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}
