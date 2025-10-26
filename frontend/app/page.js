'use client';

import { useState } from 'react';
import { ArrowUpRight, Sparkles } from 'lucide-react';

const suggestedPrompts = [
  'Find a technical co-founder who loves edge AI hardware.',
  'Match me with a growth partner who has scaled to Series B.',
  'Pair me with a product lead obsessed with B2B fintech.',
];

const proofPoints = [
  { value: '2,341', label: 'builders actively looking' },
  { value: '6 min', label: 'average first reply' },
  { value: 'Invite-only', label: 'vetted for seriousness, not vibes' },
];

export default function Home() {
  const [focused, setFocused] = useState(false);

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#05060D] text-white">
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(90,108,255,0.32),transparent_60%)]" />
        <div className="absolute left-[-12%] top-1/3 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,_rgba(42,227,241,0.28),transparent_68%)] blur-3xl opacity-80 animate-orbit-slow" />
        <div className="absolute right-[-14%] bottom-[-10%] h-[520px] w-[520px] rounded-full bg-[radial-gradient(circle,_rgba(246,170,255,0.24),transparent_70%)] blur-3xl opacity-70 animate-orbit-slow" />
        <div className="absolute inset-0 bg-synergy-grid opacity-30 mask-soft" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(5,6,13,0),rgba(5,6,13,0.92))]" />
      </div>

      <header className="fixed top-0 left-0 right-0 z-30 px-6 py-6 sm:px-10">
        <div className="mx-auto flex max-w-6xl items-center justify-between rounded-full border border-white/10 bg-white/[0.06] px-6 py-4 backdrop-blur-2xl">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#726BFF]/80 via-[#6C96FF]/70 to-[#59E3FF]/70 shadow-[0_0_25px_rgba(103,129,255,0.45)]">
              <Sparkles className="h-4 w-4 text-white" aria-hidden="true" />
            </span>
            <span className="font-heading text-lg uppercase tracking-[0.32em] text-white/80">
              Synergy
            </span>
          </div>
          <nav className="flex items-center gap-6 text-sm text-white/60">
            <a
              href="#how"
              className="transition duration-200 hover:text-white"
            >
              How it works
            </a>
            <button
              type="button"
              aria-label="Sign in"
              className="flex h-10 w-10 items-center justify-center rounded-full border border-white/15 bg-white/[0.08] backdrop-blur-md transition duration-200 hover:border-white/40 hover:bg-white/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#48D6FF]/70 focus-visible:ring-offset-2 focus-visible:ring-offset-[#05060D]"
            >
              <span className="block h-6 w-6 rounded-full bg-gradient-to-br from-white/70 to-white/15 shadow-[0_0_12px_rgba(255,255,255,0.35)]" />
            </button>
          </nav>
        </div>
      </header>

      <main className="relative flex min-h-screen flex-col items-center justify-center px-6 pb-20 pt-36 sm:px-10">
        <div className="mx-auto flex w-full max-w-5xl flex-col items-center gap-14">
          <section className="relative w-full max-w-4xl">
            <div className="absolute -inset-[1.5px] rounded-[34px] bg-gradient-to-br from-white/45 via-white/10 to-transparent opacity-50 blur-2xl" />
            <div className="relative flex flex-col gap-10 rounded-[32px] border border-white/12 bg-white/[0.05] px-8 py-12 shadow-[0_45px_120px_-45px_rgba(15,22,52,0.9)] backdrop-blur-[28px] sm:px-16 sm:py-16">
              <div
                className="flex items-center gap-2 self-start rounded-full border border-white/12 bg-white/[0.07] px-5 py-2 text-xs font-medium uppercase tracking-[0.42em] text-white/55 opacity-0 animate-fade-up"
                style={{ animationDelay: '60ms' }}
              >
                <span className="relative inline-flex h-2 w-2 items-center justify-center rounded-full bg-[#4CC6FF] shadow-[0_0_12px_rgba(78,200,255,0.8)]" />
                Private beta
              </div>
              <div
                className="space-y-3 text-left opacity-0 animate-fade-up"
                style={{ animationDelay: '140ms' }}
              >
                <h1 className="font-heading text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  Find your co-founder.
                </h1>
                <p className="max-w-xl text-base leading-relaxed text-white/70 sm:text-lg">
                  Tell Synergy what you’re building. We’ll match you with someone
                  who can build it with you.
                </p>
              </div>
              <form
                onSubmit={(event) => event.preventDefault()}
                className="space-y-6 opacity-0 animate-fade-up"
                style={{ animationDelay: '220ms' }}
              >
                <div
                  className={`relative flex items-center gap-4 rounded-full border px-6 py-5 transition-all duration-300 focus-within:border-white/60 focus-within:shadow-[0_24px_72px_-32px_rgba(88,150,255,0.95)] ${
                    focused
                      ? 'border-white/50 shadow-[0_0_0_1px_rgba(164,197,255,0.45),0_24px_72px_-30px_rgba(88,150,255,0.85)]'
                      : 'border-white/15 shadow-[0_32px_90px_-48px_rgba(8,14,36,0.9)]'
                  } bg-white/[0.08] backdrop-blur-3xl`}
                >
                  <input
                    type="text"
                    placeholder="I need a full-stack partner who can move fast on AI infra and is okay with equity-first."
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                    className="w-full bg-transparent text-base text-white placeholder:text-white/35 focus:outline-none sm:text-lg"
                    aria-label="Describe your dream co-founder"
                  />
                  <button
                    type="button"
                    aria-label="Start matching"
                    className="relative flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#706CFF] via-[#5E82FF] to-[#46D8FF] text-white shadow-[0_24px_40px_-24px_rgba(94,136,255,0.95)] transition duration-200 hover:scale-105 hover:shadow-[0_30px_50px_-20px_rgba(94,136,255,0.95)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#48D6FF]/80 focus-visible:ring-offset-2 focus-visible:ring-offset-[#05060D]"
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
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </form>
            </div>
          </section>

          <section
            id="how"
            className="w-full max-w-4xl opacity-0 animate-fade-up"
            style={{ animationDelay: '320ms' }}
          >
            <div className="rounded-[28px] border border-white/12 bg-white/[0.04] px-6 py-6 backdrop-blur-2xl shadow-[0_25px_80px_-52px_rgba(8,16,36,0.95)] sm:px-10 sm:py-7">
              <div className="flex flex-col items-stretch gap-6 text-center text-sm text-white/65 sm:flex-row sm:items-center sm:justify-between sm:gap-0 sm:text-base sm:divide-x sm:divide-white/12">
                {proofPoints.map((point) => (
                  <div key={point.label} className="flex flex-1 flex-col gap-2 px-0 sm:px-8">
                    <span className="font-heading text-2xl font-semibold text-white">
                      {point.value}
                    </span>
                    <span className="text-xs uppercase tracking-[0.28em] text-white/45">
                      {point.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
