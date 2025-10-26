'use client';

import { useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { ArrowUpRight, Sparkles } from 'lucide-react';
import config from '@/components/chatbot/config';
import MessageParser from '@/components/chatbot/MessageParser';
import ActionProvider from '@/components/chatbot/ActionProvider';

const Chatbot = dynamic(() => import('react-chatbot-kit').then(mod => mod.default), {
  ssr: false,
});

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

  const handlePromptClick = (prompt) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  };

  const ChatActionProvider = class extends ActionProvider {
    constructor(createChatBotMessage, setStateFunc) {
      super(createChatBotMessage, setStateFunc);
    }

    handleUserMessage = (message) => {
      const trimmed = message.trim();
      if (!trimmed) return;

      const replies = [
        "Logged. Anything else about your ideal partner or timeline?",
        "Understood. What qualities matter most beyond skills?",
        "Got it. Share any preferred locations or working cadence?",
        "Thanks. Are there past collaborators you’ve thrived with?",
      ];

      const response =
        replies[Math.floor(Math.random() * replies.length)] ??
        "Appreciated. Tell me more when you're ready.";

      const botMessage = this.createChatBotMessage(response);

      setTimeout(() => {
        this.setState((prev) => ({
          ...prev,
          messages: [...prev.messages, botMessage],
        }));
      }, 420);
    };
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
                onSubmit={(event) => event.preventDefault()}
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
                    placeholder="Describe your dream. I’ll match you with someone who can build it with you."
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                    value={inputValue}
                    onChange={(event) => setInputValue(event.target.value)}
                    className="w-full bg-transparent text-base text-white focus:outline-none sm:text-lg"
                    aria-label="Describe your dream co-founder"
                  />
                  <button
                    type="button"
                    aria-label="Start matching"
                    className="relative flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#706CFF] via-[#5E82FF] to-[#46D8FF] text-white shadow-[0_24px_40px_-24px_rgba(94,136,255,0.8)] transition duration-200 hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#48D6FF]/80 focus-visible:ring-offset-2 focus-visible:ring-offset-[#05060D]"
                  >
                    <ArrowUpRight className="h-5 w-5" aria-hidden="true" />
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

        <section
          id="synergy-chat"
          className="relative z-10 mt-32 w-full"
        >
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
      </main>
    </div>
  );
}
