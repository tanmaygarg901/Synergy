import { createChatBotMessage } from 'react-chatbot-kit';

const config = {
  initialMessages: [
    createChatBotMessage(
      "Hi! I'm Synergy AI. I'll help you find the perfect collaborator. Let's start - what's your name?"
    ),
  ],
  botName: 'Synergy AI',
  customStyles: {
    botMessageBox: {
      backgroundColor: '#376B7E',
    },
    chatButton: {
      backgroundColor: '#5ccc9d',
    },
  },
};

export default config;
