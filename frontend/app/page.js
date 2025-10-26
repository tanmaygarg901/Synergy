'use client';

import { useRef, useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { ArrowUpRight, Sparkles } from 'lucide-react';
import config from '@/components/chatbot/config';
import MessageParser from '@/components/chatbot/MessageParser';
import ActionProvider from '@/components/chatbot/ActionProvider';
import { sendChatMessage, findCollaborators, generateSessionId, checkBackendHealth } from '@/lib/api';
import UserCard from '@/components/UserCard';
import './chatbot.css';

const Chatbot = dynamic(() => import('react-chatbot-kit').then(mod => mod.default), {
  ssr: false,
});

const suggestedPrompts = [
  // Full info - best case demo
  "I'm a software engineer with Python and React skills, building a healthcare AI tool for doctors. Based in SF, looking for a designer co-founder to join full-time.",
  
  // Partial/ambiguous - shows AI asking clarifying questions
  "I'm interested in climate tech and renewable energy. Looking for a co-founder.",
  
  // Missing info - demonstrates conversation flow
  "Need a technical co-founder for my startup idea.",
  
  // Good balance - realistic scenario
  "Product designer with fintech experience. Want to build a B2B payments platform, need an engineer who knows backend systems.",
];

export default function Home() {
  const [focused, setFocused] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [sessionId] = useState(() => generateSessionId());
  const [chatHistory, setChatHistory] = useState([]);
  const [matches, setMatches] = useState([]);
  const [teamSuggestions, setTeamSuggestions] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [error, setError] = useState(null);
  const [chatbotKey, setChatbotKey] = useState(0);
  const [isMatching, setIsMatching] = useState(false);
  const inputRef = useRef(null);
  const chatbotRef = useRef(null);

  // Check backend connection on mount
  useEffect(() => {
    checkBackendHealth().then(setBackendConnected);
  }, []);

  // Debug: Monitor matches state changes
  useEffect(() => {
    console.log('🔄 Matches state changed:', matches.length, 'matches');
    console.log('🔄 Team suggestions state changed:', teamSuggestions.length, 'teams');
  }, [matches, teamSuggestions]);

  const handlePromptClick = (prompt) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  };

  const handleSendMessage = async () => {
    const trimmed = inputValue.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    const userMessage = trimmed;
    setInputValue('');

    try {
      // Send initial message to backend
      const response = await sendChatMessage(sessionId, userMessage);
      
      console.log('📨 TOP BOX - Backend response:', response);
      console.log('   is_trigger:', response.is_trigger);
      
      // Update chat history  
      setChatHistory(prev => {
        const newHistory = [
          ...prev,
          { role: 'user', content: userMessage },
          { role: 'assistant', content: response.response },
        ];
        
        // Check if backend triggered matching
        if (response.is_trigger === true || response.is_trigger === 'true') {
          console.log('🎯 TOP BOX - Trigger detected! Calling findCollaborators');
          setIsMatching(true);
          
          const matchingStartTime = Date.now();
          const transcript = newHistory
            .map(msg => `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`)
            .join('\n');
          
          findCollaborators(sessionId, transcript)
            .then(matchData => {
              const newMatches = matchData.matches || [];
              const newTeams = matchData.team_suggestions || [];
              const matchingDuration = Date.now() - matchingStartTime;
              const remainingTime = Math.max(0, 1500 - matchingDuration);
              
              setTimeout(() => {
                setMatches(newMatches);
                setTeamSuggestions(newTeams);
                setUserProfile(matchData.your_profile);
                setIsMatching(false);
                
                setTimeout(() => {
                  const matchesHeading = Array.from(document.querySelectorAll('h2'))
                    .find(h2 => h2.textContent.includes('Your Perfect Matches'));
                  if (matchesHeading) {
                    matchesHeading.parentElement.scrollIntoView({ 
                      behavior: 'smooth', 
                      block: 'start' 
                    });
                  }
                }, 800);
              }, remainingTime);
            })
            .catch(err => {
              console.error('❌ Error finding collaborators:', err);
              setError('Failed to find matches');
              setIsMatching(false);
            });
        }
        
        return newHistory;
      });

      // Increment chatbot key to force re-render with new history
      setChatbotKey(prev => prev + 1);

      // Scroll to chatbot section to continue conversation
      setTimeout(() => {
        const chatSection = document.getElementById('synergy-chat');
        if (chatSection) {
          // Get the section's position
          const rect = chatSection.getBoundingClientRect();
          const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
          // Scroll with offset to account for fixed navbar (100px)
          window.scrollTo({
            top: scrollTop + rect.top - 100,
            behavior: 'smooth'
          });
        }
        
        // Focus on chatbot input after scroll
        setTimeout(() => {
          const chatInput = document.querySelector('.react-chatbot-kit-chat-input');
          if (chatInput) {
            chatInput.focus();
          }
        }, 600);
      }, 300);

    } catch (error) {
      console.error('Error:', error);
      setError(error.message || 'Failed to send message. Please check if the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  // Create action provider using useMemo to avoid recreation
  const ChatActionProvider = useMemo(() => {
    return class extends ActionProvider {
      constructor(createChatBotMessage, setStateFunc, createClientMessage) {
        super(createChatBotMessage, setStateFunc, createClientMessage);
      }

      handleUserMessage = async (message) => {
        const trimmed = message.trim();
        if (!trimmed) return;

        try {
          const response = await sendChatMessage(sessionId, trimmed);
          console.log('📨 Backend response:', response);
          console.log('   is_trigger value:', response.is_trigger);
          console.log('   is_trigger type:', typeof response.is_trigger);
          
          const botMessage = this.createChatBotMessage(response.response);

          // Add bot message to chatbot
          this.setState((prev) => ({
            ...prev,
            messages: [...prev.messages, botMessage],
          }));

          // Update parent state with new messages
          setChatHistory((prev) => {
            const newHistory = [
              ...prev,
              { role: 'user', content: trimmed },
              { role: 'assistant', content: response.response },
            ];
            
            // Check for trigger after updating history
            const totalMessages = newHistory.length;
            console.log(`📊 Total messages: ${totalMessages}, is_trigger: ${response.is_trigger}`);
            
            // Trigger matching if backend confirms (removed message count requirement)
            // Backend will only set is_trigger=true when it has enough information
            // Check both boolean true and string "true" for safety
            const shouldTrigger = response.is_trigger === true || response.is_trigger === 'true';
            console.log(`🔍 Should trigger? ${shouldTrigger}`);
            
            if (shouldTrigger) {
              // Build transcript from all messages
              const transcript = newHistory
                .map(msg => `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`)
                .join('\n');

              console.log('🎯 Triggering matching with transcript');
              setIsMatching(true);
              
              // Track when matching started for minimum display time
              const matchingStartTime = Date.now();

              // Trigger matching
              findCollaborators(sessionId, transcript)
                .then(matchData => {
                  console.log('✅ Match data received:', matchData);
                  console.log('   Matches count:', matchData.matches?.length || 0);
                  console.log('   Team suggestions count:', matchData.team_suggestions?.length || 0);
                  
                  const newMatches = matchData.matches || [];
                  const newTeams = matchData.team_suggestions || [];
                  
                  // Calculate how long matching took
                  const matchingDuration = Date.now() - matchingStartTime;
                  const minDisplayTime = 1500; // 1.5 seconds minimum
                  const remainingTime = Math.max(0, minDisplayTime - matchingDuration);
                  
                  // Wait for remaining time before hiding loading indicator
                  setTimeout(() => {
                    setMatches(newMatches);
                    setTeamSuggestions(newTeams);
                    setUserProfile(matchData.your_profile);
                    setIsMatching(false);
                    
                    console.log('   State updated - matches:', newMatches.length, 'teams:', newTeams.length);
                    
                    // Scroll DOWN to matches section after they appear
                    setTimeout(() => {
                      const matchesHeading = Array.from(document.querySelectorAll('h2'))
                        .find(h2 => h2.textContent.includes('Your Perfect Matches'));
                      
                      if (matchesHeading) {
                        console.log('   Scrolling to matches section');
                        // Scroll to top of matches section
                        matchesHeading.parentElement.scrollIntoView({ 
                          behavior: 'smooth', 
                          block: 'start' 
                        });
                      } else {
                        console.log('   ⚠️ Matches heading not found in DOM');
                      }
                    }, 800);
                  }, remainingTime);
                })
                .catch(err => {
                  console.error('❌ Error finding collaborators:', err);
                  setError('Failed to find matches. Please try again.');
                  setIsMatching(false);
                });
            }
            
            return newHistory;
          });

        } catch (error) {
          console.error('Error:', error);
          const errorMessage = this.createChatBotMessage(
            'Sorry, I encountered an error. Please make sure the backend is running.'
          );
          this.setState((prev) => ({
            ...prev,
            messages: [...prev.messages, errorMessage],
          }));
        }
      };
    };
  }, [sessionId, chatHistory]);

  return (
    <div className="relative min-h-screen bg-[#05060D] text-white">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(90,108,255,0.32),transparent_60%)]" />
        <div className="absolute left-[-12%] top-1/3 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,_rgba(42,227,241,0.28),transparent_68%)] blur-3xl opacity-80 animate-orbit-slow" />
        <div className="absolute right-[-14%] bottom-[-10%] h-[520px] w-[520px] rounded-full bg-[radial-gradient(circle,_rgba(246,170,255,0.24),transparent_70%)] blur-3xl opacity-70 animate-orbit-slow" />
        <div className="absolute inset-0 bg-synergy-grid opacity-30 mask-soft" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(5,6,13,0),rgba(5,6,13,0.92))]" />
      </div>

      <header className="fixed top-0 left-0 right-0 z-30 px-4 py-6 sm:px-8">
        <div className="mx-auto flex w-full max-w-[min(1280px,calc(100%-1.5rem))] items-center justify-between rounded-full border border-white/10 bg-white/[0.06] px-6 py-4 backdrop-blur-2xl sm:px-8">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#726BFF]/80 via-[#6C96FF]/70 to-[#59E3FF]/70 shadow-[0_0_25px_rgba(103,129,255,0.45)]">
              <Sparkles className="h-4 w-4 text-white" aria-hidden="true" />
            </span>
            <span className="font-heading text-lg uppercase tracking-[0.32em] text-white/80">
              Synergy
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${backendConnected ? 'bg-green-400' : 'bg-red-400'}`} />
            <span className="text-sm text-white/60">
              {backendConnected ? 'Connected' : 'Offline'}
            </span>
          </div>
        </div>
      </header>

      <main className="relative flex min-h-screen flex-col items-center px-4 pb-16 pt-28 sm:px-8">
        {/* Debug panel - temporary */}
        <div className="fixed bottom-4 right-4 z-50 rounded-lg border border-white/20 bg-black/90 p-4 text-xs text-white backdrop-blur shadow-xl">
          <div className="font-bold mb-2 text-sm">🔍 Debug Info</div>
          <div className="space-y-1">
            <div>💬 Messages: {chatHistory.length}</div>
            <div>👥 Matches: <span className="font-bold text-green-400">{matches.length}</span></div>
            <div>🎯 Teams: <span className="font-bold text-blue-400">{teamSuggestions.length}</span></div>
            <div className={isMatching ? 'text-yellow-400 font-bold' : 'text-green-400'}>
              {isMatching ? '⏳ Matching...' : '✓ Ready'}
            </div>
          </div>
        </div>

        {/* Matching in progress indicator */}
        {isMatching && (
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50">
            <div className="rounded-2xl border border-white/20 bg-black/90 p-8 backdrop-blur-xl text-center">
              <div className="mb-4 flex justify-center">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-white/20 border-t-[#5E82FF]"></div>
              </div>
              <div className="text-lg font-semibold text-white">Finding Your Perfect Matches...</div>
              <div className="mt-2 text-sm text-white/60">Analyzing profiles and team dynamics</div>
            </div>
          </div>
        )}

        {/* Error notification */}
        {error && (
          <div className="fixed top-24 left-1/2 -translate-x-1/2 z-50 max-w-md w-full mx-4">
            <div className="rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 backdrop-blur-xl">
              <div className="flex items-center gap-2">
                <span className="text-red-400">⚠️</span>
                <p className="text-sm text-red-200">{error}</p>
                <button 
                  onClick={() => setError(null)}
                  className="ml-auto text-red-400 hover:text-red-300"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="mx-auto flex w-full max-w-[min(1280px,calc(100%-1.5rem))] flex-col items-center">
          <section id="how" className="relative w-full">
            <div className="absolute -inset-[1.5px] rounded-[34px] bg-gradient-to-br from-white/45 via-white/10 to-transparent opacity-50 blur-2xl" />
            <div className="relative mt-3 flex flex-col gap-10 rounded-[32px] border border-white/12 bg-white/[0.05] px-8 py-12 shadow-[0_45px_120px_-45px_rgba(15,22,52,0.9)] backdrop-blur-[28px] sm:mt-6 sm:px-20 sm:py-16">
              <div className="flex items-center gap-2 self-start rounded-full border border-white/12 bg-white/[0.07] px-5 py-2 text-xs font-medium uppercase tracking-[0.34em] text-white/55">
                <span className="relative inline-flex h-2 w-2 items-center justify-center rounded-full bg-[#4CC6FF] shadow-[0_0_12px_rgba(78,200,255,0.8)]" />
                Powered by Groq and ChromaDB
              </div>
              <div className="space-y-3 text-left">
                <h1 className="font-heading text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  Find your co-founder.
                </h1>
                <p className="max-w-2xl text-base leading-relaxed text-white/70 sm:text-lg md:max-w-none md:whitespace-nowrap">
                  Tell Synergy what you're building. We'll handle the search for the one.
                </p>
              </div>
              <form
                onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                className="space-y-6"
              >
                <div
                  className={`relative flex items-center gap-4 rounded-full border border-white/15 px-6 py-5 transition-all duration-300 focus-within:border-[1.6px] focus-within:border-white/60 ${
                    focused
                      ? 'shadow-[0_0_0_1px_rgba(164,197,255,0.45)]'
                      : 'shadow-[0_30px_80px_-50px_rgba(8,14,36,0.9)]'
                  } bg-white/[0.08] backdrop-blur-3xl`}
                >
                  <input
                    type="text"
                    ref={inputRef}
                    placeholder="Describe your dream. I'll match you with someone who can build it with you."
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    disabled={isLoading || !backendConnected}
                    className="w-full bg-transparent text-base text-white focus:outline-none sm:text-lg disabled:opacity-50"
                    aria-label="Describe your dream co-founder"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !backendConnected}
                    aria-label="Start matching"
                    className="relative flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#706CFF] via-[#5E82FF] to-[#46D8FF] text-white shadow-[0_24px_40px_-24px_rgba(94,136,255,0.8)] transition duration-200 hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#48D6FF]/80 focus-visible:ring-offset-2 focus-visible:ring-offset-[#05060D] disabled:opacity-50 disabled:hover:scale-100"
                  >
                    {isLoading ? (
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    ) : (
                      <ArrowUpRight className="h-5 w-5" aria-hidden="true" />
                    )}
                  </button>
                </div>
                <div className="flex flex-wrap gap-3">
                  {suggestedPrompts.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      disabled={isLoading || !backendConnected}
                      className="rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm text-white/70 transition duration-200 hover:-translate-y-0.5 hover:border-white/40 hover:text-white hover:shadow-[0_18px_40px_-28px_rgba(102,146,255,0.85)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#48D6FF]/70 focus-visible:ring-offset-2 focus-visible:ring-offset-[#05060D] sm:px-5 sm:py-2.5 sm:text-base disabled:opacity-50 disabled:hover:translate-y-0"
                      onClick={() => handlePromptClick(prompt)}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </form>
            </div>
          </section>
        </div>

        <section
          id="synergy-chat"
          className="relative z-10 mt-32 w-full"
        >
          <div className="mx-auto flex max-w-6xl flex-col items-center gap-5 text-center">
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-5 py-1 text-xs font-medium uppercase tracking-[0.32em] text-white/55 transition-all duration-300 hover:border-white/20 hover:bg-white/[0.08]">
              Continue the conversation
            </span>
            <h2 className="font-heading text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Chat with Synergy AI
            </h2>
            <p className="max-w-2xl text-sm leading-relaxed text-white/60 sm:text-base">
              Share more context and Synergy will refine co-founder matches in real time.
            </p>
          </div>
          <div className="synergy-chat mx-auto mt-12 w-full max-w-7xl px-0 transition-all duration-500">
            <Chatbot
              config={config(chatHistory)}
              messageParser={MessageParser}
              actionProvider={ChatActionProvider}
              placeholderText="Tell Synergy what you need next..."
              headerText="Synergy AI"
              validator={(input) => input.trim().length > 0}
              key={chatbotKey}
            />
          </div>
        </section>

        {/* Display matches and team suggestions - appears AFTER chatbot */}
        {matches && matches.length > 0 && (
          <div className="mx-auto w-full max-w-[min(1280px,calc(100%-1.5rem))] mt-16 mb-16">
            <section className="w-full">
              <h2 className="mb-8 text-center font-heading text-3xl font-semibold text-white animate-fade-in">
                Your Perfect Matches
              </h2>
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {matches.map((match, idx) => (
                  <div
                    key={idx}
                    className="animate-slide-up opacity-0"
                    style={{
                      animationDelay: `${idx * 100}ms`,
                      animationFillMode: 'forwards'
                    }}
                  >
                    <UserCard collaborator={match} />
                  </div>
                ))}
              </div>
            </section>

            {/* Display team suggestions */}
            {teamSuggestions && teamSuggestions.length > 0 && (
              <section className="mt-16 w-full animate-fade-in" style={{ animationDelay: '400ms' }}>
                <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-8 backdrop-blur-xl transition-all duration-500 hover:border-white/20">
                  <h2 className="mb-6 text-center font-heading text-2xl font-semibold text-white">
                    🎯 Suggested Teams
                  </h2>
                  <p className="mb-8 text-center text-sm text-white/60">
                    Based on your profile, here are some powerful team combinations
                  </p>
                  <div className="space-y-6">
                    {teamSuggestions.map((team, idx) => {
                      // Extract member names from objects
                      const memberNames = team.members?.map(m => m.name || 'Unknown').join(' + ') || 'Team';
                      const memberRoles = team.members?.map(m => m.role || 'Unknown').join(' + ') || '';
                      
                      return (
                        <div
                          key={idx}
                          className="rounded-2xl border border-white/10 bg-white/[0.05] p-6 transition-all duration-300 hover:border-white/20 hover:bg-white/[0.08] hover:scale-[1.02] hover:shadow-lg animate-slide-up opacity-0"
                          style={{
                            animationDelay: `${500 + idx * 150}ms`,
                            animationFillMode: 'forwards'
                          }}
                        >
                          <div className="mb-3 flex items-center gap-3">
                            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[#726BFF] to-[#5E82FF] text-sm font-bold text-white">
                              {idx + 1}
                            </span>
                            <div>
                              <h3 className="font-semibold text-white">
                                You + {memberNames}
                              </h3>
                              <p className="text-xs text-white/50 mt-1">
                                {memberRoles}
                              </p>
                            </div>
                          </div>
                          <p className="text-sm leading-relaxed text-white/70">
                            {team.reasoning || `A balanced team combining ${memberRoles.split(' + ').join(', ')} skills for your project.`}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
