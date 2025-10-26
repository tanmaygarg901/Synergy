'use client';

import { useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { ArrowUpRight, Loader2, Sparkles } from 'lucide-react';
import config from '@/components/chatbot/config';
import MessageParser from '@/components/chatbot/MessageParser';
import ActionProvider from '@/components/chatbot/ActionProvider';
import UserCard from '@/components/UserCard';

const Chatbot = dynamic(() => import('react-chatbot-kit').then(mod => mod.default), {
  ssr: false,
});

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

const suggestedPrompts = [
  'I need a full-stack partner who can move fast on AI infra and is okay with equity-first.',
  'Find a technical co-founder who loves edge AI hardware.',
  'Match me with a growth partner who has scaled to Series B.',
  'Pair me with a product lead obsessed with B2B fintech.',
];

export default function Home() {
  const [focused, setFocused] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef(null);
  const sessionIdRef = useRef(
    `session_${Date.now().toString(36)}_${Math.random().toString(16).slice(2)}`
  );
  const actionProviderRef = useRef(null);
  const createMatchState = () => ({
    status: 'idle',
    profile: null,
    matches: [],
    suggestions: [],
    userId: null,
    error: null,
  });
  const [matchState, setMatchState] = useState(createMatchState);
  const [composerSending, setComposerSending] = useState(false);

  const handlePromptClick = (prompt) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  };

  const buildTranscript = (messages) =>
    messages
      .map((msg) => `${msg.type === 'bot' ? 'Assistant' : 'User'}: ${msg.message}`)
      .join('\n');

  const formatTeamSuggestion = (suggestion, index) => {
    if (!suggestion) {
      return `Team ${index + 1}`;
    }

    if (typeof suggestion === 'string') {
      return suggestion;
    }

    if (suggestion.summary) {
      return suggestion.summary;
    }

    if (Array.isArray(suggestion.members) && suggestion.members.length > 0) {
      const label = suggestion.team_name || `Team ${index + 1}`;
      const roster = suggestion.members
        .map((member) => {
          const name = member?.name || 'Match';
          const role = member?.role ? ` (${member.role})` : '';
          return `${name}${role}`;
        })
        .join(' + ');
      return `${label}: ${roster}`;
    }

    return `Team ${index + 1}`;
  };

  const fetchMatchData = async (transcript) => {
    setMatchState({
      status: 'loading',
      profile: null,
      matches: [],
      suggestions: [],
      userId: null,
      error: null,
    });

    try {
      const response = await fetch(`${API_URL}/find-collaborators`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_transcript: transcript,
          session_id: sessionIdRef.current,
        }),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.error || 'Unable to find collaborators right now.');
      }

      const data = await response.json();
      setMatchState({
        status: 'ready',
        profile: data.your_profile || null,
        matches: data.matches || [],
        suggestions: data.team_suggestions || [],
        userId: data.user_id || null,
        error: null,
      });
      sessionIdRef.current = `session_${Date.now().toString(36)}_${Math.random()
        .toString(16)
        .slice(2)}`;
    } catch (error) {
      console.error('find-collaborators error:', error);
      setMatchState({
        status: 'error',
        profile: null,
        matches: [],
        suggestions: [],
        userId: null,
        error: error.message || 'Unexpected error finding collaborators.',
      });
    }
  };

  const ChatActionProvider = class extends ActionProvider {
    constructor(createChatBotMessage, setStateFunc, createClientMessage, stateRef) {
      super(createChatBotMessage, setStateFunc, createClientMessage, stateRef);
      actionProviderRef.current = this;
    }

    handleUserMessage = async (message, options = {}) => {
      const trimmed = message.trim();
      if (!trimmed) {
        const warn = this.createChatBotMessage("I didn't catch that—could you share a bit more?");
        this.setState((prev) => ({
          ...prev,
          messages: [...prev.messages, warn],
        }));
        return;
      }

      if (options.addClientMessage && this.createClientMessage) {
        const clientMessage = this.createClientMessage(trimmed);
        this.setState((prev) => ({
          ...prev,
          messages: [...prev.messages, clientMessage],
        }));
        if (this.stateRef && Array.isArray(this.stateRef.messages)) {
          this.stateRef.messages = [...this.stateRef.messages, clientMessage];
        }
      }

      setMatchState((prev) => {
        if (prev.status === 'idle' || prev.status === 'loading') {
          return prev;
        }
        return createMatchState();
      });

      try {
        const response = await fetch(`${API_URL}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: trimmed,
            session_id: sessionIdRef.current,
          }),
        });

        if (!response.ok) {
          const payload = await response.json().catch(() => ({}));
          throw new Error(payload.error || 'Unable to reach Synergy right now.');
        }

        const data = await response.json();
        const botMessage = this.createChatBotMessage(data.response);

        this.setState((prev) => ({
          ...prev,
          messages: [...prev.messages, botMessage],
        }));

        if (data.is_trigger) {
          const existing = (this.stateRef && this.stateRef.messages) || [];
          const hasUserInHistory = existing.some(
            (item) => item?.type === 'user' && item?.message === trimmed
          );
          const history = hasUserInHistory
            ? [...existing]
            : [...existing, { type: 'user', message: trimmed }];
          const conversation = [...history, { type: 'bot', message: data.response }];
          const transcript = buildTranscript(conversation);
          await fetchMatchData(transcript);
        }
      } catch (error) {
        console.error('chat error:', error);
        const fallback = this.createChatBotMessage(
          error.message?.includes('Failed to fetch')
            ? "I'm having trouble connecting. Check the backend and try again."
            : error.message || 'Something went wrong. Try again in a moment.'
        );
        this.setState((prev) => ({
          ...prev,
          messages: [...prev.messages, fallback],
        }));
      }
    };
  };

  const deliverToChatbot = async (message, options, attempt = 0) => {
    const provider = actionProviderRef.current;
    if (provider) {
      await provider.handleUserMessage(message, options);
      return true;
    }

    if (attempt >= 20) {
      return false;
    }

    await new Promise((resolve) => setTimeout(resolve, 120));
    return deliverToChatbot(message, options, attempt + 1);
  };

  const sendThroughChatWidget = (text) => {
    const input =
      document.querySelector('.react-chatbot-kit-chat-input') ||
      document.querySelector('.react-chatbot-kit-chat-message-input');
    const sendButton = document.querySelector('.react-chatbot-kit-chat-btn-send');

    if (!input || !sendButton) {
      return false;
    }

    const setNativeValue = (element, value) => {
      const tagName = element.tagName;
      let setter;
      if (tagName === 'TEXTAREA') {
        setter =
          Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
      } else {
        setter =
          Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
      }
      if (setter) {
        setter.call(element, value);
      } else {
        element.value = value;
      }
    };

    setNativeValue(input, text);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    sendButton.click();
    return true;
  };

  const handleComposerSubmit = async (event) => {
    event.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed || composerSending) {
      return;
    }

    setComposerSending(true);
    try {
      const widgetSent = sendThroughChatWidget(trimmed);
      let sent = widgetSent;

      if (!widgetSent) {
        sent = await deliverToChatbot(trimmed, { addClientMessage: true });
      }

      if (sent) {
        setInputValue('');
      } else {
        setMatchState({
          status: 'error',
          profile: null,
          matches: [],
          suggestions: [],
          userId: null,
          error: 'Synergy is still initializing. Try again in a moment.',
        });
      }
    } catch (error) {
      console.error('composer submission error:', error);
      setMatchState({
        status: 'error',
        profile: null,
        matches: [],
        suggestions: [],
        userId: null,
        error: 'Unable to send message. Please try again.',
      });
    } finally {
      setComposerSending(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#05060D] text-white">
      <div className="absolute inset-0 -z-10">
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
          <div className="h-8 w-8" aria-hidden="true" />
        </div>
      </header>

      <main className="relative flex min-h-screen flex-col items-center px-4 pb-32 pt-28 sm:px-8">
        <div className="mx-auto flex w-full max-w-[min(1280px,calc(100%-1.5rem))] flex-col items-center">
          <section id="how" className="relative w-full">
            <div className="absolute -inset-[1.5px] rounded-[34px] bg-gradient-to-br from-white/45 via-white/10 to-transparent opacity-50 blur-2xl" />
            <div className="relative mt-3 flex flex-col gap-10 rounded-[32px] border border-white/12 bg-white/[0.05] px-8 py-12 shadow-[0_45px_120px_-45px_rgba(15,22,52,0.9)] backdrop-blur-[28px] sm:mt-6 sm:px-20 sm:py-16">
              <div
                className="flex items-center gap-2 self-start rounded-full border border-white/12 bg-white/[0.07] px-5 py-2 text-xs font-medium uppercase tracking-[0.34em] text-white/55 opacity-0 animate-fade-up"
                style={{ animationDelay: '60ms' }}
              >
                <span className="relative inline-flex h-2 w-2 items-center justify-center rounded-full bg-[#4CC6FF] shadow-[0_0_12px_rgba(78,200,255,0.8)]" />
                Powered by Groq and ChromaDB
              </div>
              <div
                className="space-y-3 text-left opacity-0 animate-fade-up"
                style={{ animationDelay: '140ms' }}
              >
                <h1 className="font-heading text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  Find your co-founder.
                </h1>
                <p className="max-w-2xl text-base leading-relaxed text-white/70 sm:text-lg md:max-w-none md:whitespace-nowrap">
                  Tell Synergy what you’re building. We’ll handle the search for the one.
                </p>
              </div>
              <form
                onSubmit={handleComposerSubmit}
                className="space-y-6 opacity-0 animate-fade-up"
                style={{ animationDelay: '220ms' }}
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
                    placeholder="Describe your dream co-founder. I’ll introduce you."
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                    value={inputValue}
                    onChange={(event) => setInputValue(event.target.value)}
                    className="w-full bg-transparent text-base text-white focus:outline-none sm:text-lg"
                    aria-label="Describe your dream co-founder"
                  />
                  <button
                    type="submit"
                    aria-label="Start matching"
                    disabled={composerSending || !inputValue.trim()}
                    className="relative flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#706CFF] via-[#5E82FF] to-[#46D8FF] text-white shadow-[0_24px_40px_-24px_rgba(94,136,255,0.8)] transition duration-200 hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#48D6FF]/80 focus-visible:ring-offset-2 focus-visible:ring-offset-[#05060D] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
                  >
                    {composerSending ? (
                      <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
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
                      className="rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm text-white/70 transition duration-200 hover:-translate-y-0.5 hover:border-white/40 hover:text-white hover:shadow-[0_18px_40px_-28px_rgba(102,146,255,0.85)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#48D6FF]/70 focus-visible:ring-offset-2 focus-visible:ring-offset-[#05060D] sm:px-5 sm:py-2.5 sm:text-base"
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

        <section id="synergy-chat" className="relative z-10 mt-32 w-full">
          <div className="mx-auto flex max-w-4xl flex-col items-center gap-5 text-center">
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-5 py-1 text-xs font-medium uppercase tracking-[0.32em] text-white/55">
              Continue the conversation
            </span>
            <h2 className="font-heading text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Chat with Synergy AI
            </h2>
            <p className="max-w-2xl text-sm leading-relaxed text-white/60 sm:text-base">
              Share more context and Synergy will refine co-founder matches in real time.
            </p>
          </div>
          <div className="synergy-chat mx-auto mt-12 w-full max-w-5xl px-0">
            <Chatbot
              config={config}
              messageParser={MessageParser}
              actionProvider={ChatActionProvider}
              placeholderText="Tell Synergy what you need next..."
              headerText="Synergy AI"
              validator={(input) => input.trim().length > 0}
            />
          </div>
        </section>

        {matchState.status !== 'idle' && (
          <section className="relative z-10 mt-20 w-full">
            <div className="mx-auto flex max-w-5xl flex-col gap-10 rounded-[32px] border border-white/10 bg-white/[0.04] px-8 py-10 text-white backdrop-blur-2xl shadow-[0_40px_120px_-60px_rgba(10,14,40,0.85)] sm:px-16">
              {matchState.status === 'loading' && (
                <div className="flex flex-col items-center gap-4 text-center text-white/70">
                  <Loader2 className="h-10 w-10 animate-spin text-[#46D8FF]" />
                  <div>
                    <h3 className="font-heading text-2xl">Matching in progress</h3>
                    <p className="text-sm text-white/60">
                      Synergy is reviewing your profile and searching the network.
                    </p>
                  </div>
                </div>
              )}

              {matchState.status === 'error' && (
                <div className="rounded-2xl border border-red-400/40 bg-red-500/10 px-6 py-5 text-center text-sm text-red-200">
                  {matchState.error}
                </div>
              )}

              {matchState.status === 'ready' && (
                <>
                  <div className="space-y-3 text-center">
                    <h3 className="font-heading text-3xl">Your concierge brief</h3>
                    <p className="text-white/60">
                      Synergy captured what you shared and found collaborators who complement it.
                    </p>
                  </div>

                  {matchState.profile && (
                    <div className="rounded-3xl border border-white/12 bg-white/[0.06] p-6 shadow-[0_28px_80px_-60px_rgba(20,32,68,0.9)] sm:p-8">
                      <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
                        <div className="space-y-2 text-left">
                          <p className="text-sm uppercase tracking-[0.35em] text-white/45">Founder profile</p>
                          <h4 className="font-heading text-2xl text-white">{matchState.profile.name}</h4>
                          <p className="text-sm text-white/60">
                            Looking for <span className="text-white/80">{matchState.profile.looking_for}</span>
                          </p>
                          {matchState.userId && (
                            <p className="text-xs text-white/30">Profile ID: {matchState.userId}</p>
                          )}
                        </div>
                        <div className="grid gap-4 text-left text-sm sm:grid-cols-2">
                          <div>
                            <p className="mb-1 text-xs uppercase tracking-[0.2em] text-white/45">Skills</p>
                            <div className="flex flex-wrap gap-2">
                              {matchState.profile.skills?.map((skill, idx) => (
                                <span
                                  key={`${skill}-${idx}`}
                                  className="rounded-full border border-white/15 bg-white/[0.08] px-3 py-1 text-xs text-white/75"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div>
                            <p className="mb-1 text-xs uppercase tracking-[0.2em] text-white/45">Interests</p>
                            <div className="flex flex-wrap gap-2">
                              {matchState.profile.interests?.map((interest, idx) => (
                                <span
                                  key={`${interest}-${idx}`}
                                  className="rounded-full border border-white/15 bg-white/[0.08] px-3 py-1 text-xs text-white/75"
                                >
                                  {interest}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="space-y-6">
                    <div className="flex flex-col gap-2 text-left">
                      <h4 className="font-heading text-2xl text-white">Top matches</h4>
                      <p className="text-sm text-white/55">
                        Curated from Synergy’s private network and ranked for complementary skills.
                      </p>
                    </div>

                    {matchState.matches.length > 0 ? (
                      <div className="grid gap-6 md:grid-cols-2">
                        {matchState.matches.map((match) => (
                          <UserCard key={match.id || match.name} collaborator={match} />
                        ))}
                      </div>
                    ) : (
                      <div className="rounded-2xl border border-white/12 bg-white/[0.04] px-6 py-8 text-center text-sm text-white/60">
                        No direct matches yet. Try sharing more context or adjust what you’re looking for.
                      </div>
                    )}
                  </div>

                  {matchState.suggestions?.length > 0 && (
                    <div className="space-y-4">
                      <h4 className="font-heading text-xl text-white">Suggested team configurations</h4>
                      <ul className="space-y-3 text-sm text-white/70">
                        {matchState.suggestions.map((suggestion, index) => (
                          <li
                            key={`${suggestion?.team_name || 'team'}-${index}`}
                            className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-4"
                          >
                            {formatTeamSuggestion(suggestion, index)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
