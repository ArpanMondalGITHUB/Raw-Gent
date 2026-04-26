import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { AppSidebar } from '../../components/AppSidebar';

describe('AppSidebar', () => {
  it('renders branding, search, navigation sections, and task limit', () => {
    render(<AppSidebar />);

    expect(screen.getByText('Raw-Gent')).toBeInTheDocument();
    expect(screen.getByText('beta')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search for repos or tasks')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /recent tasks/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /codebases/i })).toBeInTheDocument();
    expect(screen.getByText('Daily task limit (0/60)')).toBeInTheDocument();
  });

  it('allows task and codebase sections to be toggled', () => {
    render(<AppSidebar />);

    fireEvent.click(screen.getByRole('button', { name: /recent tasks/i }));
    fireEvent.click(screen.getByRole('button', { name: /codebases/i }));

    expect(screen.getByRole('button', { name: /recent tasks/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /codebases/i })).toBeInTheDocument();
  });
});
