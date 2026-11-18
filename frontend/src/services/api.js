
const API_BASE_URL = "http://127.0.0.1:8000";

// Send a chat message
export const sendMessage = async (patientId, question, conversationId = null) => {
  const response = await fetch(`${API_BASE_URL}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      patient_id: patientId,
      question,
      top_k: 3,
      conversation_id: conversationId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to send message");
  }

  return response.json();
};

// Fetch previous conversations
export const getConversations = async (patientId) => {
  const response = await fetch(
    `${API_BASE_URL}/conversations/?patient_id=${encodeURIComponent(patientId)}`
  );

  if (!response.ok) {
    throw new Error("Failed to load conversations");
  }

  return response.json();
};

// Fetch messages from a conversation
export const getConversation = async (conversationId, patientId) => {
  const response = await fetch(
    `${API_BASE_URL}/conversations/${encodeURIComponent(conversationId)}?patient_id=${encodeURIComponent(patientId)}`
  );

  if (!response.ok) {
    throw new Error("Failed to load conversation");
  }

  return response.json();
};

// Delete a conversation
export const deleteConversation = async (conversationId, patientId) => {
  const response = await fetch(
    `${API_BASE_URL}/conversations/${encodeURIComponent(conversationId)}?patient_id=${encodeURIComponent(patientId)}`,
    { method: "DELETE" }
  );

  if (!response.ok) {
    throw new Error("Failed to delete conversation");
  }

  return response.json();
};
