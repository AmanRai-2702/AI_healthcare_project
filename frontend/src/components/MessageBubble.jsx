
import { Bot, User, FileText, ShieldCheck } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      <div className={`message-avatar ${isUser ? "user-avatar" : "ai-avatar"}`}>
        {isUser ? <User size={19} /> : <Bot size={20} />}
      </div>

      <div className="message-content">
        <div className="message-author">
          {isUser ? "You" : "MedFusion AI"}
          {!isUser && <span className="ai-label">AI Assistant</span>}
        </div>

        <div className="message-text">
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || ""}
            </ReactMarkdown>
          )}
        </div>

        {!isUser && message.sources?.length > 0 && (
          <div className="sources-container">
            <div className="sources-heading">
              <FileText size={15} />
              <strong>Medical sources used</strong>
            </div>

            {message.sources.map((source, index) => (
              <div className="source-item" key={index}>
                <FileText size={14} />
                <span>
                  {source.document_name ||
                    source.source_id ||
                    `Source ${index + 1}`}
                </span>
              </div>
            ))}
          </div>
        )}

        {!isUser && (
          <div className="medical-disclaimer">
            <ShieldCheck size={13} />
            AI-generated information. Not a substitute for professional medical advice.
          </div>
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
