import { GoogleGenAI, Type } from "@google/genai";

const getAiClient = () => {
  const apiKey = process.env.API_KEY;
  if (!apiKey) throw new Error("API_KEY not set");
  return new GoogleGenAI({ apiKey });
};

export const getFinancialAdvice = async (
  query: string, 
  userContext: string
): Promise<string> => {
  try {
    const ai = getAiClient();
    
    const systemInstruction = `You are a friendly, encouraging financial tutor for students using the CTFLife platform. 
    Your goal is to explain financial concepts simply (savings, compound interest, budgeting) and encourage good habits.
    
    Context about the user: ${userContext}
    
    Keep answers concise (under 100 words) and engaging. Use emojis occasionally.`;

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: query,
      config: {
        systemInstruction: systemInstruction,
      },
    });

    return response.text || "I couldn't generate a response right now.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "I'm connected to the simulator, but I need a valid API Key to think! (Check process.env.API_KEY)";
  }
};

// Feature: Analyze Receipt Image
export const analyzeReceiptImage = async (base64Image: string): Promise<any> => {
  try {
    const ai = getAiClient();
    
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview', // Stronger model for vision
      contents: {
        parts: [
          { inlineData: { mimeType: 'image/png', data: base64Image } },
          { text: "Analyze this receipt. Extract the store name, total amount, and infer the category (Food, Shopping, Transport, Entertainment, Savings). Return JSON." }
        ]
      },
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            storeName: { type: Type.STRING },
            amount: { type: Type.NUMBER },
            category: { type: Type.STRING, enum: ["Food", "Shopping", "Transport", "Entertainment", "Savings"] },
            date: { type: Type.STRING, description: "YYYY-MM-DD format" }
          },
          required: ["storeName", "amount", "category", "date"]
        }
      }
    });

    return JSON.parse(response.text || "{}");
  } catch (error) {
    console.error("Receipt Analysis Error:", error);
    return null;
  }
};

// Feature: Generate Dynamic Quiz
export const generateQuizQuestions = async (topic: string): Promise<any> => {
  try {
    const ai = getAiClient();
    
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `Generate 2 multiple choice questions about ${topic} for a student.`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              id: { type: Type.INTEGER },
              question: { type: Type.STRING },
              options: { type: Type.ARRAY, items: { type: Type.STRING } },
              correctIndex: { type: Type.INTEGER },
              explanation: { type: Type.STRING }
            },
            required: ["id", "question", "options", "correctIndex", "explanation"]
          }
        }
      }
    });

    return JSON.parse(response.text || "[]");
  } catch (error) {
    console.error("Quiz Gen Error:", error);
    return [];
  }
};