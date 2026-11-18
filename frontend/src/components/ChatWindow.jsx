
import { useEffect, useRef } from "react";
import { Bot, Sparkles, Activity } from "lucide-react";
import MessageBubble from "./MessageBubble";

function ChatWindow({
  messages = [],
  loading = false,
  onSuggestionClick,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const suggestions = [
    {
      title: "Understand my reports",
      question: "Can you explain my latest blood report?",
    },
    {
      title: "Explore my health history",
      question: "What medical information is available in my records?",
    },
    {
      title: "Understand test results",
      question: "What does my hemoglobin result mean?",
    },
    {
      title: "Prepare for my doctor",
      question: "What questions should I ask my doctor about my report?",
    },
  ];

  return (
    <div className="chat-window">
      {messages.length === 0 ? (
        <div className="welcome-screen">
          <div className="welcome-icon">
            <Activity size={34} />
          </div>

          <div className="welcome-badge">
            <Sparkles size={14} />
            Your AI Health Companion
          </div>

          <h1>
            Your health journey,
            <br />
            <span>understood better.</span>
          </h1>

          <p className="welcome-description">
            Ask questions about your medical records and health reports.
            MedFusion AI helps you understand the information in your records.
          </p>

          <div className="suggestion-heading">
            <Bot size={17} />
            Try asking
          </div>

          <div className="suggestion-grid">
            {suggestions.map((item) => (
              <button
                type="button"
                className="suggestion-card"
                key={item.title}
                onClick={() => onSuggestionClick?.(item.question)}
                disabled={loading}
              >
                <strong>{item.title}</strong>
                <p>{item.question}</p>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="messages-container">
          {messages.map((message, index) => (
            <MessageBubble
              key={message.id || index}
              message={message}
            />
          ))}

          {loading && (
            <div className="typing-indicator">
              <div className="message-avatar ai-avatar">
                <Bot size={20} />
              </div>

              <div className="typing-dots">
                <span />
                <span />
                <span />
                <p>MedFusion AI is thinking...</p>
              </div>
            </div>
          )}
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

export default ChatWindow;
