import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import HelloWorld from '../../src/components/HelloWorld';

describe('HelloWorld', () => {
  it('should render "Hello, World!"', () => {
    render(<HelloWorld />);
    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
  });
});
