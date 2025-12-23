export interface User {
  id: number;
  username: string;
  email: string;
  nickname: string;
  avatar_url: string | null;
  bio: string | null;
  created_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  nickname: string;
  password: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Couple {
  id: number;
  invite_code: string;
  anniversary_date: string | null;
  theme_color: string;
}

export interface Message {
  id: number;
  content: string;
  message_type: string;
  sender_id: number;
  receiver_id: number;
  room_id: number;
  created_at: string;
}

export interface Photo {
  id: number;
  filename: string;
  url: string;
  thumbnail_url: string | null;
  caption: string | null;
  user_id: number;
  created_at: string;
}

export interface Diary {
  id: number;
  title: string;
  content: string;
  mood: string | null;
  user_id: number;
  created_at: string;
  updated_at: string | null;
}

export interface Todo {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  due_date: string | null;
  user_id: number;
  created_at: string;
  completed_at: string | null;
}
