import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import React from 'react';

const mocks = vi.hoisted(() => ({
  loginWithGitHub: vi.fn(),
}));

vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => <div data-testid="hero-canvas">{children}</div>,
}));

vi.mock('@react-three/drei', () => ({
  OrbitControls: () => <div data-testid="orbit-controls" />,
}));

vi.mock('../../components/Hero3DScene', () => ({
  default: () => <div data-testid="hero-scene" />,
}));

vi.mock('../../components/CodeAnimation', () => ({
  default: () => <div data-testid="code-animation" />,
}));

vi.mock('../../components/FeatureCards', () => ({
  default: () => <div data-testid="feature-cards" />,
}));

vi.mock('../../services/auth', () => ({
  loginWithGitHub: mocks.loginWithGitHub,
}));

import Index from '../../pages/Index';

beforeEach(() => {
  vi.clearAllMocks();
});

describe('Index page', () => {
  it('renders the landing page sections', () => {
    render(<Index />);

    expect(screen.getByText('Raw-Gent AI')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'AI Code Agent' })).toBeInTheDocument();
    expect(screen.getByText(/reviews, builds, tests, and debugs/i)).toBeInTheDocument();
    expect(screen.getByTestId('hero-canvas')).toBeInTheDocument();
    expect(screen.getByTestId('hero-scene')).toBeInTheDocument();
    expect(screen.getByTestId('code-animation')).toBeInTheDocument();
    expect(screen.getByTestId('feature-cards')).toBeInTheDocument();
  });

  it('starts GitHub login from the top get started button', () => {
    render(<Index />);

    fireEvent.click(screen.getByRole('button', { name: 'Get Started' }));

    expect(mocks.loginWithGitHub).toHaveBeenCalledTimes(1);
  });

  it('renders stats and final CTA content', () => {
    render(<Index />);

    expect(screen.getByText('99.9%')).toBeInTheDocument();
    expect(screen.getByText('10x')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByText('24/7')).toBeInTheDocument();
    expect(screen.getByText('Ready to Transform Your Code?')).toBeInTheDocument();
  });
});
