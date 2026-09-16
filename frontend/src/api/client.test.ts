import { describe, it, expect, beforeEach } from 'vitest';
import { apiClient } from './client';
import MockAdapter from 'axios-mock-adapter';

describe('API Client Interceptors', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  afterEach(() => {
    mock.restore();
  });

  it('adds Authorization header if token exists', async () => {
    localStorage.setItem('civilcortex_token', 'fake-jwt-token');
    
    mock.onGet('/test').reply(config => {
      return [200, { headers: config.headers }];
    });

    const response = await apiClient.get('/test');
    expect(response.data.headers.Authorization).toBe('Bearer fake-jwt-token');
    
    localStorage.removeItem('civilcortex_token');
  });

  it('formats structured CivilCortexError properly on 400', async () => {
    mock.onGet('/error').reply(400, {
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid input provided',
        request_id: 'req-123'
      }
    });

    try {
      await apiClient.get('/error');
    } catch (err: any) {
      expect(err.civilCortexMessage).toBe('Invalid input provided');
      expect(err.civilCortexCode).toBe('VALIDATION_ERROR');
    }
  });

  it('falls back to generic error message if structure is missing', async () => {
    mock.onGet('/error').reply(500, 'Internal Server Error');

    try {
      await apiClient.get('/error');
    } catch (err: any) {
      // Typically it falls back to Axios error or detailed string
      expect(err).toBeDefined();
      expect(err.response.status).toBe(500);
    }
  });
});
