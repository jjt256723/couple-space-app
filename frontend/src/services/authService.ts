import { apiClient } from './api';
import type { UserCreate, UserLogin, Token, User } from '../types';

export const authService = {
  async register(data: UserCreate): Promise<User> {
    const response = await apiClient.clientInstance.post<User>('/auth/register', data);
    return response.data;
  },

  async login(data: UserLogin): Promise<Token> {
    const response = await apiClient.clientInstance.post<Token>('/auth/login', data);
    await apiClient.setAuthTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  },

  async logout() {
    await apiClient.clearAuthTokens();
  },

  async refreshTokens(): Promise<Token> {
    const response = await apiClient.clientInstance.post<Token>('/auth/refresh');
    await apiClient.setAuthTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  },
};
