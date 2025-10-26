import { createChatBotMessage, createClientMessage } from 'react-chatbot-kit';

const config = (chatHistory = []) => {
  // If there's chat history, use it; otherwise show default message
  const initialMessages = chatHistory.length > 0
    ? [
        createChatBotMessage(
          "Hi! I'm Synergy AI. Tell me about yourself - your skills, interests, and what kind of co-founder you're looking for."
        ),
        ...chatHistory.flatMap(msg => {
          if (msg.role === 'user') {
            return [createClientMessage(msg.content)];
          } else {
            return [createChatBotMessage(msg.content)];
          }
        })
      ]
    : [
        createChatBotMessage(
          "Hi! I'm Synergy AI. Tell me about yourself - your skills, interests, and what kind of co-founder you're looking for."
        ),
      ];

  return {
    initialMessages,
    botName: 'Synergy AI',
    customStyles: {
      botMessageBox: {
        backgroundColor: 'rgba(94, 130, 255, 0.15)',
        border: '1px solid rgba(94, 130, 255, 0.3)',
        color: '#ffffff',
        borderRadius: '16px 16px 16px 4px',
        padding: '14px 18px',
        maxWidth: '75%',
        boxShadow: '0 4px 16px rgba(94, 130, 255, 0.15)',
        fontSize: '15px',
        lineHeight: '1.5',
      },
      chatButton: {
        backgroundColor: '#5E82FF',
        borderRadius: '50%',
        width: '60px',
        height: '60px',
        boxShadow: '0 8px 24px rgba(94, 130, 255, 0.4)',
      },
      userMessageBox: {
        backgroundColor: '#726BFF',
        color: '#ffffff',
        borderRadius: '16px 16px 4px 16px',
        padding: '14px 18px',
        maxWidth: '75%',
        boxShadow: '0 4px 16px rgba(114, 107, 255, 0.25)',
        fontSize: '15px',
        lineHeight: '1.5',
      },
    },
    customComponents: {},
  };
};

export default config;
