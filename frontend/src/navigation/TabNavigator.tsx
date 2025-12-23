import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import ChatScreen from '../screens/chat/ChatScreen';
import AlbumListScreen from '../screens/album/AlbumListScreen';
import DiaryListScreen from '../screens/diary/DiaryListScreen';
import TodoScreen from '../screens/todo/TodoScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';

const Tab = createBottomTabNavigator();

export default function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,
        tabBarActiveTintColor: '#FF6B6B',
        tabBarInactiveTintColor: '#999',
      }}
    >
      <Tab.Screen
        name="Chat"
        component={ChatScreen}
        options={{ title: '聊天' }}
      />
      <Tab.Screen
        name="Album"
        component={AlbumListScreen}
        options={{ title: '相册' }}
      />
      <Tab.Screen
        name="Diary"
        component={DiaryListScreen}
        options={{ title: '日记' }}
      />
      <Tab.Screen
        name="Todo"
        component={TodoScreen}
        options={{ title: '待办' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: '我的' }}
      />
    </Tab.Navigator>
  );
}
