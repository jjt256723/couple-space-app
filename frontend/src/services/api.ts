import axios, { AxiosInstance, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private async getToken(): Promise<string | null> {
    return await AsyncStorage.getItem('access_token');
  }

  private async setToken(token: string) {
    await AsyncStorage.setItem('access_token', token);
  }

  private async removeToken() {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
  }

  private setupInterceptors() {
    this.client.interceptors.request.use(
      async (config) => {
        const token = await this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = await AsyncStorage.getItem('refresh_token');
            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
              headers: { Authorization: `Bearer ${refreshToken}` },
            });

            const { access_token, refresh_token } = response.data;
            await this.setToken(access_token);
            await AsyncStorage.setItem('refresh_token', refresh_token);

            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            await this.removeToken();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  public async setAuthTokens(accessToken: string, refreshToken: string) {
    await this.setToken(accessToken);
    await AsyncStorage.setItem('refresh_token', refreshToken);
  }

  public async clearAuthTokens() {
    await this.removeToken();
  }

  get clientInstance() {
    return this.client;
  }
}

export const apiClient = new ApiClient();
