import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import React from 'react';

vi.mock('@monaco-editor/react', () => ({
  DiffEditor: (props: { original?: string; modified?: string; language?: string }) => (
    <div
      data-testid="diff-editor"
      data-original={props.original}
      data-modified={props.modified}
      data-language={props.language}
    />
  ),
}));

vi.mock('react-resizable-panels', () => ({
  PanelGroup: ({ children }: { children: React.ReactNode }) => <div data-testid="panel-group">{children}</div>,
  Panel: ({ children }: { children: React.ReactNode }) => <section>{children}</section>,
  PanelResizeHandle: () => <div data-testid="panel-resize-handle" />,
}));

import { Chatui } from '../../components/Chatui';
import { JobStatusResponse } from '../../schemas/run_agent.schemas';

const messages = [
  {
    role: 'user' as const,
    content: 'Please fix this',
    timestamp: '2026-04-26T10:00:00.000Z',
  },
  {
    role: 'agent' as const,
    content: 'All done',
    timestamp: '2026-04-26T10:01:00.000Z',
  },
];

const jobStatus: JobStatusResponse = {
  job_id: 'job-1',
  status: 'completed',
  messages,
  file_changes: [
    {
      file_path: 'src/new.ts',
      original_content: null,
      modified_content: 'new file',
      change_type: 'created',
      language: 'typescript',
    },
    {
      file_path: 'src/app.ts',
      original_content: 'old app',
      modified_content: 'new app',
      change_type: 'modified',
      language: 'typescript',
    },
  ],
  current_step: 'Done',
  created_at: '2026-04-26T10:00:00.000Z',
};

describe('Chatui', () => {
  it('renders job status, messages, file tabs, and selected diff', () => {
    render(<Chatui jobStatus={jobStatus} messages={messages} onSendMessage={vi.fn()} isConnected />);

    expect(screen.getByText('Task updates')).toBeInTheDocument();
    expect(screen.getByText('job-1')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
    expect(screen.getByText('Ready for review')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create pr/i })).toBeInTheDocument();
    expect(screen.getByText('Please fix this')).toBeInTheDocument();
    expect(screen.getAllByText('All done')).toHaveLength(2);
    expect(screen.getByText('app.ts')).toBeInTheDocument();
    expect(screen.getByText('new.ts')).toBeInTheDocument();
    expect(screen.getByTestId('diff-editor')).toHaveAttribute('data-original', 'old app');
  });

  it('requests PR creation from the review panel', () => {
    const onCreatePr = vi.fn();
    render(
      <Chatui
        jobStatus={jobStatus}
        messages={messages}
        onSendMessage={vi.fn()}
        onCreatePr={onCreatePr}
        isConnected
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: /create pr/i }));

    expect(onCreatePr).toHaveBeenCalledTimes(1);
  });

  it('sends trimmed messages on enter and clears the input', () => {
    const onSendMessage = vi.fn();
    render(<Chatui jobStatus={jobStatus} messages={messages} onSendMessage={onSendMessage} isConnected />);

    const input = screen.getByPlaceholderText('Type a message and hit enter...');
    fireEvent.change(input, { target: { value: '  keep going  ' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(onSendMessage).toHaveBeenCalledWith('keep going');
    expect(input).toHaveValue('');
  });

  it('does not send when disconnected', () => {
    const onSendMessage = vi.fn();
    render(
      <Chatui
        jobStatus={{ ...jobStatus, status: 'running' }}
        messages={[]}
        onSendMessage={onSendMessage}
        isConnected={false}
      />,
    );

    const input = screen.getByPlaceholderText('Type a message and hit enter...');
    fireEvent.change(input, { target: { value: 'hello' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(onSendMessage).not.toHaveBeenCalled();
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });

  it('shows empty states when there are no messages or file changes', () => {
    render(<Chatui jobStatus={null} messages={[]} onSendMessage={vi.fn()} isConnected={false} />);

    expect(screen.getByText('No job selected')).toBeInTheDocument();
    expect(screen.getByText('Unknown')).toBeInTheDocument();
    expect(screen.getByText('No messages yet.')).toBeInTheDocument();
    expect(screen.getByText('No file changes detected yet.')).toBeInTheDocument();
    expect(screen.getByText('No file selected')).toBeInTheDocument();
  });
});
