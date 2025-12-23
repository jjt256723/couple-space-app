import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function DiaryListScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>日记功能开发中...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    fontSize: 16,
    color: '#999',
  },
});
