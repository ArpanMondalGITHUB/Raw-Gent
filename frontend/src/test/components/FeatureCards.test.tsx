import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import FeatureCards from '../../components/FeatureCards';

describe('FeatureCards', () => {
  it('renders all feature titles and descriptions', () => {
    render(<FeatureCards />);

    expect(screen.getByText('Smart Code Review')).toBeInTheDocument();
    expect(screen.getByText('Feature Development')).toBeInTheDocument();
    expect(screen.getByText('Automated Testing')).toBeInTheDocument();
    expect(screen.getByText('Bug Detection & Fix')).toBeInTheDocument();
    expect(screen.getByText(/AI-powered analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/Transform ideas into production-ready code/i)).toBeInTheDocument();
    expect(screen.getByText(/Generate comprehensive test suites/i)).toBeInTheDocument();
    expect(screen.getByText(/Identify and resolve bugs/i)).toBeInTheDocument();
  });
});
