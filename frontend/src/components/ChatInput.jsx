
import { useState } from "react";
import { Send, Paperclip, Sparkles } from "lucide-react";

function ChatInput({ onSendMessage, loading = false }) {
  const [message, setMessage] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) return;

    onSendMessage(trimmedMessage);
    setMessage("");
  };

  return (
    <div className="chat-input-wrapper">
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <button
          type="button"
          className="attachment-btn"
          title="Upload medical documents (coming soon)"
          disabled
        >
          <Paperclip size={20} />
        </button>

        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask anything about your health records..."
          rows={1}
          disabled={loading}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
        />

        <button
          type="submit"
          className="send-btn"
          disabled={!message.trim() || loading}
          title="Send message"
        >
          <Send size={19} />
        </button>
      </form>

      <div className="input-footer">
        <span>
          <Sparkles size={13} />
          Powered by MedFusion AI
        </span>
        <span>Enter to send · Shift + Enter for new line</span>
      </div>
    </div>
  );
}

export default ChatInput;
