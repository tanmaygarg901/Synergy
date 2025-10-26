const fallbackClientMessage = (content) => ({
  id: `user_${Date.now().toString(36)}_${Math.random().toString(16).slice(2)}`,
  message: content,
  type: 'user',
});

class ActionProvider {
  constructor(createChatBotMessage, setStateFunc, createClientMessage, stateRef) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
    this.createClientMessage = createClientMessage || fallbackClientMessage;
    this.stateRef = stateRef;
  }

  handleUserMessage = async (message) => {
    // To be overridden by consumers
  };
}

export default ActionProvider;
