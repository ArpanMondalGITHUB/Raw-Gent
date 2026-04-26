import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Navbar } from '../../components/Navbar';

describe('Navbar', () => {
  it('renders repository label and toolbar actions', () => {
    render(<Navbar />);

    expect(screen.getByText(/heloo world/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /feedback/i })).toBeInTheDocument();
    expect(screen.getAllByRole('button')).toHaveLength(4);
  });
});
