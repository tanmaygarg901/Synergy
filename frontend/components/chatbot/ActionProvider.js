class ActionProvider {
  constructor(createChatBotMessage, setStateFunc, createClientMessage, stateRef) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
    this.createClientMessage = createClientMessage;
    this.stateRef = stateRef;
  }

  handleUserMessage = async (message) => {
    // This will be called by the parent component
    // which handles the actual API call
  };
}

export default ActionProvider;
