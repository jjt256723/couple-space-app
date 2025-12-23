import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { User } from '../../types';
import { authService } from '../../services/authService';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
  error: null,
};

export const register = createAsyncThunk(
  'auth/register',
  async (userData: { username: string; email: string; nickname: string; password: string }) => {
    const response = await authService.register(userData);
    return response;
  }
);

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { username: string; password: string }) => {
    const tokenData = await authService.login(credentials);
    return tokenData;
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  await authService.logout();
});

export const loadUserFromStorage = createAsyncThunk('auth/loadUserFromStorage', async () => {
  const token = await AsyncStorage.getItem('access_token');
  const userJson = await AsyncStorage.getItem('user');
  const user = userJson ? JSON.parse(userJson) : null;
  return { token, user };
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '注册失败';
      })
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '登录失败';
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      .addCase(loadUserFromStorage.fulfilled, (state, action) => {
        state.token = action.payload.token;
        state.user = action.payload.user;
        state.isAuthenticated = !!(action.payload.token && action.payload.user);
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
