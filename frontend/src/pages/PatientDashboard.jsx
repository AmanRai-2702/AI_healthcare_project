
import { useCallback, useEffect, useState } from "react";
import { Menu, X, AlertCircle } from "lucide-react";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";

import {
  sendMessage,
  getConversations,
  getConversation,
  deleteConversation,
} from "../services/api";

const PATIENT_ID = "patient-001";

function PatientDashboard() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Load conversation history from backend
  const loadConversations = useCallback(async () => {
    try {
      const data = await getConversations(PATIENT_ID);

      const items = Array.isArray(data)
        ? data
        : data.conversations || data.items || [];

      setConversations(items);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Start a new conversation
  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setError("");
    setSidebarOpen(false);
  };

  // Load a previous conversation
  const handleSelectConversation = async (conversationId) => {
    try {
      setError("");
      setLoading(true);

      const data = await getConversation(conversationId, PATIENT_ID);

      const history = Array.isArray(data)
        ? data
        : data.messages || [];

      setMessages(
        history.map((message) => ({
          id: message.id,
          role: message.role,
          content: message.content,
          sources: message.sources || [],
        }))
      );

      setActiveConversationId(conversationId);
      setSidebarOpen(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete a conversation
  const handleDeleteConversation = async (conversationId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this conversation?"
    );

    if (!confirmed) return;

    try {
      await deleteConversation(conversationId, PATIENT_ID);

      if (activeConversationId === conversationId) {
        handleNewChat();
      }

      await loadConversations();
    } catch (err) {
      setError(err.message);
    }
  };

  // Send a message to the AI backend
  const handleSendMessage = async (question) => {
    const userMessage = {
      id: Date.now(),
      role: "user",
      content: question,
    };

    setMessages((previous) => [...previous, userMessage]);
    setLoading(true);
    setError("");

    try {
      const response = await sendMessage(
        PATIENT_ID,
        question,
        activeConversationId
      );

      setActiveConversationId(response.conversation_id);

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.answer,
        sources: response.sources || [],
      };

      setMessages((previous) => [...previous, assistantMessage]);

      await loadConversations();
    } catch (err) {
      setError(err.message);

      // Remove the unsaved user message if the request failed
      setMessages((previous) =>
        previous.filter((message) => message.id !== userMessage.id)
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-layout">

      {/* Mobile sidebar toggle */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
      </button>

      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className={sidebarOpen ? "sidebar-mobile-open" : "sidebar-wrapper"}>
        <Sidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          onNewChat={handleNewChat}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
        />
      </div>

      <main className="main-content">
        <header className="top-header">
          <div>
            <p className="header-label">PATIENT PORTAL</p>
            <h2>AI Health Assistant</h2>
          </div>

          <div className="header-status">
            <span className="status-dot" />
            AI Assistant Online
          </div>
        </header>

        {error && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
            <button onClick={() => setError("")}>Dismiss</button>
          </div>
        )}

        <ChatWindow
          messages={messages}
          loading={loading}
          onSuggestionClick={handleSendMessage}
        />

        <ChatInput
          onSendMessage={handleSendMessage}
          loading={loading}
        />
      </main>
    </div>
  );
}

export default PatientDashboard;
