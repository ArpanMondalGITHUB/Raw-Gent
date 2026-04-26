import { render } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('@react-three/fiber', () => ({
  useFrame: vi.fn(),
}));

import Hero3DScene from '../../components/Hero3DScene';

beforeEach(() => {
  vi.spyOn(console, 'error').mockImplementation(() => {});
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('Hero3DScene', () => {
  it('renders lights, particles, and main meshes', () => {
    const { container } = render(<Hero3DScene />);

    expect(container.querySelectorAll('mesh').length).toBeGreaterThanOrEqual(205);
    expect(container.querySelectorAll('ambientlight')).toHaveLength(1);
    expect(container.querySelectorAll('pointlight')).toHaveLength(2);
  });
});
