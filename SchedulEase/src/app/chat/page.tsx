"use client";

import { useState, useEffect } from "react";
import { Send } from "lucide-react";
import axios from "axios";
import { Toaster } from "@/components/ui/toaster"
import { useToast } from "@/hooks/use-toast";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface Venue {
  name: string;
  address: string;
  capacity: string;
  features: string[];
  source: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId] = useState(crypto.randomUUID());
  const [venues, setVenues] = useState<Venue[]>([]);
  const { toast } = useToast();

  const handleInitialMessage = async () => {
    try {
      const { data } = await axios.post(
        "http://localhost:8000/api/ai_message",
        {
          message: "start",
          conversation_id: conversationId
        }
      );
      
      const aiMessage: Message = {
        role: "assistant",
        content: data.message,
        timestamp: new Date(),
      };
      setMessages([aiMessage]);
    } catch (error) {
      console.error("Failed to start conversation:", error);
    }
  };

  useEffect(() => {
    handleInitialMessage();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const { data } = await axios.post(
        "http://localhost:8000/api/ai_message",
        {
          message: input.trim(),
          conversation_id: conversationId
        }
      );

      if (data.type === "venues") {
        setVenues(data.venues);
      }

      const aiMessage: Message = {
        role: "assistant",
        content: data.message,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);

    } catch (error) {
      console.error("Failed to send message:", error);
      toast({
        description: "Failed to send message. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 p-4 shadow-sm">
        <div className="max-w-3xl mx-auto flex items-center justify-center">
          <h1 className="text-xl font-semibold text-gray-800 dark:text-white">
            Event Planning Assistant
          </h1>
        </div>
      </div>

      {/* Chat container */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-3xl h-full mx-auto flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`
                    max-w-[80%] px-4 py-2 rounded-2xl shadow-sm
                    ${
                      message.role === "user"
                        ? "bg-blue-600 text-white rounded-br-none"
                        : "bg-white dark:bg-gray-800 rounded-bl-none border dark:border-gray-700"
                    }
                  `}
                >
                  <div className={`text-sm ${
                    message.role === "user" ? "text-white" : "text-gray-800 dark:text-gray-200"
                  }`}>
                    {message.content}
                  </div>
                </div>
              </div>
            ))}

            {/* Venue Recommendations */}
            {venues.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                {venues.map((venue, index) => (
                  <div key={index} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                    <h3 className="font-semibold text-lg">{venue.name}</h3>
                    <p className="text-gray-600 dark:text-gray-400">{venue.address}</p>
                    <p className="text-sm">{venue.capacity}</p>
                    <div className="mt-2">
                      <p className="text-sm font-semibold">Features:</p>
                      <ul className="text-sm list-disc list-inside">
                        {venue.features.map((feature, idx) => (
                          <li key={idx}>{feature}</li>
                        ))}
                      </ul>
                    </div>
                    <a 
                      href={venue.source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 text-sm hover:underline mt-2 inline-block"
                    >
                      More Info
                    </a>
                  </div>
                ))}
              </div>
            )}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 px-4 py-2 rounded-2xl rounded-bl-none border dark:border-gray-700">
                  <span className="text-gray-400 dark:text-gray-500 animate-pulse">
                    Typing...
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Input form */}
          <div className="p-4 bg-white dark:bg-gray-800 border-t dark:border-gray-700">
            <form
              onSubmit={handleSubmit}
              className="max-w-3xl mx-auto flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 p-3 bg-gray-100 dark:bg-gray-900 border dark:border-gray-700 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading}
                className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </div>
      <Toaster />
    </div>
  );
}
