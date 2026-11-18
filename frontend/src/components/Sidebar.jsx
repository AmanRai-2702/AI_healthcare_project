
import {
  Activity,
  MessageSquare,
  Plus,
  Trash2,
  PanelLeftClose,
  ShieldCheck,
  Stethoscope,
} from "lucide-react";

function Sidebar({
  conversations = [],
  activeConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Activity size={23} />
        </div>
        <div>
          <h2>MedFusion <span>AI</span></h2>
          <p>Healthcare Intelligence</p>
        </div>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        <Plus size={19} />
        <span>New conversation</span>
      </button>

      <div className="sidebar-section">
        <p className="section-heading">WORKSPACE</p>

        <div className="sidebar-nav-item active">
          <MessageSquare size={18} />
          <span>AI Assistant</span>
        </div>
      </div>

      <div className="conversation-section">
        <p className="section-heading">RECENT CONVERSATIONS</p>

        <div className="conversation-list">
          {conversations.length === 0 ? (
            <p className="empty-conversations">
              Your conversations will appear here.
            </p>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.conversation_id}
                className={`conversation-item ${
                  activeConversationId === conversation.conversation_id
                    ? "selected"
                    : ""
                }`}
                onClick={() =>
                  onSelectConversation(conversation.conversation_id)
                }
              >
                <MessageSquare size={16} />

                <span className="conversation-title">
                  {conversation.title || "New conversation"}
                </span>

                <button
                  className="delete-chat-btn"
                  title="Delete conversation"
                  onClick={(event) => {
                    event.stopPropagation();
                    onDeleteConversation(conversation.conversation_id);
                  }}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="sidebar-bottom">
        <div className="privacy-card">
          <ShieldCheck size={20} />
          <div>
            <strong>Privacy first</strong>
            <p>Your health conversations are kept separate by patient ID.</p>
          </div>
        </div>

        <div className="profile-card">
          <div className="profile-avatar">
            <Stethoscope size={20} />
          </div>
          <div>
            <strong>Demo Patient</strong>
            <p>Patient account</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
