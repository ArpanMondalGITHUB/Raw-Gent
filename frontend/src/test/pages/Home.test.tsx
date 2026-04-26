import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('../../components/AppSidebar', () => ({
  AppSidebar: () => <aside data-testid="app-sidebar">Sidebar</aside>,
}));

vi.mock('../../components/MainContent', () => ({
  MainContent: () => <main data-testid="main-content">Main content</main>,
}));

vi.mock('../../components/TopBar', () => ({
  TopBar: () => <header data-testid="top-bar">Top bar</header>,
}));

import Home from '../../pages/Home';

describe('Home page', () => {
  it('composes the sidebar, main content, and top bar', () => {
    render(<Home />);

    expect(screen.getByTestId('app-sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('main-content')).toBeInTheDocument();
    expect(screen.getByTestId('top-bar')).toBeInTheDocument();
  });
});
