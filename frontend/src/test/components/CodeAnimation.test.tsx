import { act, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import CodeAnimation from '../../components/CodeAnimation';

afterEach(() => {
  vi.useRealTimers();
});

describe('CodeAnimation', () => {
  it('renders the first code snippet', () => {
    vi.useFakeTimers();
    render(<CodeAnimation />);

    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText(/optimizePerformance/)).toBeInTheDocument();
  });

  it('cycles to the next snippet over time', () => {
    vi.useFakeTimers();
    render(<CodeAnimation />);

    act(() => {
      vi.advanceTimersByTime(3300);
    });

    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText(/calculate_average/)).toBeInTheDocument();
  });
});
