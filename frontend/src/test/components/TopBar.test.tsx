import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { TopBar } from '../../components/TopBar';

describe('TopBar', () => {
  it('renders feedback, settings, and profile controls', () => {
    const { container } = render(<TopBar />);

    expect(screen.getByRole('button', { name: /feedback/i })).toBeInTheDocument();
    expect(screen.getAllByRole('button')).toHaveLength(2);
    expect(container.querySelector('.rounded-full')).toBeInTheDocument();
  });
});
