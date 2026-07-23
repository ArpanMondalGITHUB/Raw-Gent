import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../config/runtime', () => ({
  WS_BASE_URL: 'wss://socket.rawgent.test',
}));

import { useWebsocket } from '../hooks/ws_hooks';

const statusPayload = {
  job_id: 'job-1',
  status: 'running',
  messages: [
    {
      role: 'agent',
      content: 'Working on it',
      timestamp: '2026-04-26T10:00:00.000Z',
    },
  ],
  file_changes: [],
  created_at: '2026-04-26T10:00:00.000Z',
};

class MockWebSocket {
  static OPEN = 1;

  static instances: MockWebSocket[] = [];

  url: string;
  readyState = MockWebSocket.OPEN;
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: (() => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  send = vi.fn((message: string) => {
    this.sent.push(message);
  });

  close = vi.fn(() => {
    this.readyState = 3;
    this.onclose?.();
  });

  emitOpen() {
    this.onopen?.();
  }

  emitMessage(message: unknown) {
    this.onmessage?.({ data: JSON.stringify(message) } as MessageEvent);
  }

  emitError() {
    this.onerror?.();
  }
}

beforeEach(() => {
  MockWebSocket.instances = [];
  vi.stubGlobal('WebSocket', MockWebSocket);
  vi.spyOn(console, 'log').mockImplementation(() => {});
  vi.spyOn(console, 'warn').mockImplementation(() => {});
  vi.spyOn(console, 'error').mockImplementation(() => {});
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('useWebsocket', () => {
  it('does not connect without a job id', () => {
    renderHook(() => useWebsocket(null));

    expect(MockWebSocket.instances).toHaveLength(0);
  });

  it('connects to the encoded job websocket URL', () => {
    renderHook(() => useWebsocket('job/with spaces'));

    expect(MockWebSocket.instances[0].url).toBe(
      'wss://socket.rawgent.test/ws/status/job%2Fwith%20spaces',
    );
  });

  it('marks the hook as connected on open', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));

    act(() => MockWebSocket.instances[0].emitOpen());

    expect(result.current.isConnected).toBe(true);
  });

  it('responds to ping messages with pong', () => {
    renderHook(() => useWebsocket('job-1'));
    const ws = MockWebSocket.instances[0];

    act(() => ws.emitMessage({ type: 'ping' }));

    expect(JSON.parse(ws.sent[0])).toMatchObject({ type: 'pong' });
  });

  it('updates job status and messages from status updates', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));

    act(() =>
      MockWebSocket.instances[0].emitMessage({
        type: 'status_update',
        content: JSON.stringify(statusPayload),
        job_id: 'job-1',
        timestamp: '2026-04-26T10:00:01.000Z',
      }),
    );

    expect(result.current.jobStatus?.status).toBe('running');
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].content).toBe('Working on it');
  });

  it('appends agent messages', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));

    act(() =>
      MockWebSocket.instances[0].emitMessage({
        type: 'agent_message',
        content: 'Finished',
        job_id: 'job-1',
        timestamp: '2026-04-26T10:00:02.000Z',
      }),
    );

    expect(result.current.messages).toEqual([
      {
        role: 'agent',
        content: 'Finished',
        timestamp: '2026-04-26T10:00:02.000Z',
      },
    ]);
  });

  it('appends user messages', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));

    act(() =>
      MockWebSocket.instances[0].emitMessage({
        type: 'user_message',
        content: 'Continue',
        job_id: 'job-1',
        timestamp: '2026-04-26T10:00:03.000Z',
      }),
    );

    expect(result.current.messages[0]).toMatchObject({ role: 'user', content: 'Continue' });
  });

  it('ignores invalid websocket messages', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));

    act(() => MockWebSocket.instances[0].emitMessage({ type: 'agent_message' }));

    expect(result.current.messages).toEqual([]);
  });

  it('sends user messages when connected', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));
    const ws = MockWebSocket.instances[0];

    act(() => result.current.onSendMessage('Please continue'));

    expect(JSON.parse(ws.sent[0])).toMatchObject({
      type: 'user_message',
      content: 'Please continue',
      job_id: 'job-1',
    });
  });

  it('sends create PR commands when connected', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));
    const ws = MockWebSocket.instances[0];

    act(() => result.current.onCreatePr());

    expect(JSON.parse(ws.sent[0])).toMatchObject({
      type: 'create_pr',
      content: 'yes',
      job_id: 'job-1',
    });
  });

  it('does not send messages when the socket is not open', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));
    const ws = MockWebSocket.instances[0];
    ws.readyState = 0;

    act(() => result.current.onSendMessage('Please continue'));

    expect(ws.sent).toHaveLength(0);
  });

  it('marks disconnected on socket errors and close', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));
    const ws = MockWebSocket.instances[0];

    act(() => ws.emitOpen());
    expect(result.current.isConnected).toBe(true);

    act(() => ws.emitError());
    expect(result.current.isConnected).toBe(false);

    act(() => ws.close());
    expect(result.current.isConnected).toBe(false);
  });

  it('disconnect closes the websocket', () => {
    const { result } = renderHook(() => useWebsocket('job-1'));
    const ws = MockWebSocket.instances[0];

    act(() => result.current.disconnect());

    expect(ws.close).toHaveBeenCalled();
  });
});
