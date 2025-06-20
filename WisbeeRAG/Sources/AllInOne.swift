import SwiftUI
import AppKit
import ObjectBox
import LangChain
import Foundation

// MARK: - API Client

// Wisbee API Client - OpenAI Compatible (using Groq)
class WisbeeAPIClient {
    private let apiKey: String
    private let baseURL: String
    private let session: URLSession
    
    init(apiKey: String, baseURL: String = "https://api.groq.com/openai/v1") {
        self.apiKey = apiKey
        self.baseURL = baseURL
        self.session = URLSession.shared
    }
    
    // Chat completion request
    func chatCompletion(messages: [ChatMessage], model: String = "llama3-8b-8192", temperature: Double = 0.7, maxTokens: Int = 150) async throws -> ChatCompletionResponse {
        let url = URL(string: "\(baseURL)/chat/completions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody = ChatCompletionRequest(
            model: model,
            messages: messages.map { OpenAIMessage(role: $0.isUser ? "user" : "assistant", content: $0.content) },
            temperature: temperature,
            maxTokens: maxTokens
        )
        
        request.httpBody = try JSONEncoder().encode(requestBody)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            if let errorData = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
                throw APIError.apiError(message: errorData.error.message)
            }
            throw APIError.httpError(statusCode: httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(ChatCompletionResponse.self, from: data)
    }
}

// API Models
struct ChatCompletionRequest: Codable {
    let model: String
    let messages: [OpenAIMessage]
    let temperature: Double
    let maxTokens: Int
    
    enum CodingKeys: String, CodingKey {
        case model, messages, temperature
        case maxTokens = "max_tokens"
    }
}

struct OpenAIMessage: Codable {
    let role: String
    let content: String
}

struct ChatCompletionResponse: Codable {
    let id: String
    let object: String
    let created: Int
    let model: String
    let choices: [Choice]
    let usage: Usage?
    
    struct Choice: Codable {
        let index: Int
        let message: OpenAIMessage
        let finishReason: String?
        
        enum CodingKeys: String, CodingKey {
            case index, message
            case finishReason = "finish_reason"
        }
    }
    
    struct Usage: Codable {
        let promptTokens: Int
        let completionTokens: Int
        let totalTokens: Int
        
        enum CodingKeys: String, CodingKey {
            case promptTokens = "prompt_tokens"
            case completionTokens = "completion_tokens"
            case totalTokens = "total_tokens"
        }
    }
}

struct APIErrorResponse: Codable {
    let error: APIErrorDetail
    
    struct APIErrorDetail: Codable {
        let message: String
        let type: String
    }
}

enum APIError: LocalizedError {
    case invalidResponse
    case httpError(statusCode: Int)
    case apiError(message: String)
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid API response"
        case .httpError(let statusCode):
            return "HTTP error: \(statusCode)"
        case .apiError(let message):
            return "API error: \(message)"
        case .decodingError:
            return "Failed to decode response"
        }
    }
}

// MARK: - Vector Document

// Vector document model for ObjectBox
class VectorDocument: Entity {
    var id: Id = 0
    var content: String = ""
    // Store embedding as Data since ObjectBox 1.9 doesn't support [Float] directly
    var embeddingData: Data = Data()
    var metadata: String = ""
    
    // Computed property for easy access
    var embedding: [Float] {
        get {
            guard !embeddingData.isEmpty else { return [] }
            return embeddingData.withUnsafeBytes { bytes in
                Array(bytes.bindMemory(to: Float.self))
            }
        }
        set {
            embeddingData = newValue.withUnsafeBytes { bytes in
                Data(bytes)
            }
        }
    }
    
    required init() {}
    
    init(content: String, embedding: [Float], metadata: String = "") {
        self.content = content
        self.embedding = embedding
        self.metadata = metadata
    }
}

// MARK: - Retriever

// Custom Retriever implementation for ObjectBox
class ObjectBoxRetriever {
    private var documents: [VectorDocument]
    let topK: Int
    
    init(documents: [VectorDocument], topK: Int = 5) {
        self.documents = documents
        self.topK = topK
    }
    
    func retrieve(query: String) throws -> [VectorDocument] {
        // Simple retrieval - return top K documents
        // In production, implement proper similarity search
        return Array(documents.prefix(topK))
    }
}

// MARK: - Agent

// Wisbee Agent with Tool Support
class WisbeeAgent {
    let llm: String // Placeholder for LLM
    let retriever: ObjectBoxRetriever
    private var apiClient: WisbeeAPIClient?
    
    init(modelPath: String, retriever: ObjectBoxRetriever) {
        self.llm = modelPath
        self.retriever = retriever
    }
    
    // Set API client for real API calls
    func setAPIClient(_ client: WisbeeAPIClient) {
        self.apiClient = client
    }
    
    func run(question: String) async throws -> String {
        // If API client is available, use it
        if let apiClient = apiClient {
            return try await runWithAPI(question: question, apiClient: apiClient)
        }
        
        // Otherwise, use mock response
        print("🤔 Processing (Mock): \(question)")
        
        // 1. Retrieve relevant documents
        let docs = try retriever.retrieve(query: question)
        
        // 2. Build context
        let context = docs.map { $0.content }.joined(separator: "\n")
        
        // 3. Generate prompt
        let prompt = """
        Context:
        \(context)
        
        Question: \(question)
        
        Answer based on the context above:
        """
        
        // 4. LLM inference (placeholder)
        print("📝 Prompt:\n\(prompt)")
        
        // Mock response
        let response = """
        Wisbeeの主な特徴は以下の通りです：
        1. 世界初のText-to-LoRA技術を搭載
        2. jan-nano XSモデル（Q4_K_XS量子化）による高速推論
        3. 70以上のカテゴリーで学習された豊富な知識
        """
        
        return response
    }
    
    // Use real API for processing
    func runWithAPI(question: String, apiClient: WisbeeAPIClient) async throws -> String {
        print("🤔 Processing with Wisbee API: \(question)")
        
        // 1. Retrieve relevant documents
        let docs = try retriever.retrieve(query: question)
        
        // 2. Build context
        let context = docs.map { $0.content }.joined(separator: "\n")
        
        // 3. Create messages
        var messages: [ChatMessage] = []
        
        // System message with context
        let systemPrompt = """
        You are Wisbee (ウィズビー), a helpful AI assistant that always responds in Japanese.
        あなたはWisbeeです。親切で知識豊富なAIアシスタントです。必ず日本語で回答してください。
        以下のコンテキストを参考に質問に答えてください：
        
        Context:
        \(context)
        """
        messages.append(ChatMessage(content: systemPrompt, isUser: false))
        
        // User question
        messages.append(ChatMessage(content: question, isUser: true))
        
        // 4. Call API
        let response = try await apiClient.chatCompletion(
            messages: messages,
            temperature: 0.7,
            maxTokens: 300
        )
        
        // 5. Extract response
        guard let firstChoice = response.choices.first else {
            throw WisbeeError.invalidResponse
        }
        
        return firstChoice.message.content
    }
    
    // Run with specific model
    func runWithModel(question: String, model: String) async throws -> String {
        guard let apiClient = apiClient else {
            return try await run(question: question) // Fallback to mock
        }
        
        print("🤔 Processing with \(model): \(question)")
        
        // 1. Retrieve relevant documents
        let docs = try retriever.retrieve(query: question)
        
        // 2. Build context
        let context = docs.map { $0.content }.joined(separator: "\n")
        
        // 3. Create messages
        var messages: [ChatMessage] = []
        
        // System message with context
        let systemPrompt = """
        You are Wisbee (ウィズビー), a helpful AI assistant that always responds in Japanese.
        あなたはWisbeeです。親切で知識豊富なAIアシスタントです。必ず日本語で回答してください。
        以下のコンテキストを参考に質問に答えてください：
        
        Context:
        \(context)
        """
        messages.append(ChatMessage(content: systemPrompt, isUser: false))
        
        // User question
        messages.append(ChatMessage(content: question, isUser: true))
        
        // 4. Call API with specific model
        let response = try await apiClient.chatCompletion(
            messages: messages,
            model: model,
            temperature: 0.7,
            maxTokens: 300
        )
        
        // 5. Extract response
        guard let firstChoice = response.choices.first else {
            throw WisbeeError.invalidResponse
        }
        
        return firstChoice.message.content
    }
}

// Error types
enum WisbeeError: LocalizedError {
    case invalidResponse
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid API response"
        }
    }
}

// MARK: - Chat UI

// Message model
struct ChatMessage: Identifiable {
    let id = UUID()
    let content: String
    let isUser: Bool
    let timestamp = Date()
}

// Modern Message Bubble View
struct ModernMessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            if !message.isUser {
                // AI Avatar
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.yellow.opacity(0.8), Color.orange.opacity(0.8)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 32, height: 32)
                    
                    Text("🐝")
                        .font(.system(size: 16))
                }
            }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 8) {
                HStack {
                    if !message.isUser {
                        Text("Wisbee")
                            .font(.caption)
                            .fontWeight(.medium)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Text(timeString(from: message.timestamp))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                Text(message.content)
                    .font(.body)
                    .lineLimit(nil)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(message.isUser ? 
                                  LinearGradient(
                                    colors: [Color.blue, Color.blue.opacity(0.8)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                  ) :
                                  LinearGradient(
                                    colors: [Color.secondary.opacity(0.2), Color.secondary.opacity(0.3)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                  )
                            )
                    )
                    .foregroundColor(message.isUser ? .white : .primary)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.secondary.opacity(0.4).opacity(0.3), lineWidth: 0.5)
                    )
            }
            .frame(maxWidth: .infinity, alignment: message.isUser ? .trailing : .leading)
            
            if message.isUser {
                // User Avatar
                Circle()
                    .fill(Color.blue.opacity(0.8))
                    .frame(width: 32, height: 32)
                    .overlay(
                        Image(systemName: "person.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.white)
                    )
            }
        }
        .padding(.horizontal, message.isUser ? 24 : 0)
    }
    
    private func timeString(from date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// Modern Loading Indicator
struct ModernLoadingIndicator: View {
    @State private var animating = false
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            // AI Avatar
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.yellow.opacity(0.8), Color.orange.opacity(0.8)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 32, height: 32)
                
                Text("🐝")
                    .font(.system(size: 16))
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Wisbee")
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
                
                HStack(spacing: 6) {
                    ForEach(0..<3) { index in
                        Circle()
                            .fill(Color.blue.opacity(0.6))
                            .frame(width: 8, height: 8)
                            .scaleEffect(animating ? 1.2 : 0.8)
                            .animation(
                                Animation.easeInOut(duration: 0.8)
                                    .repeatForever()
                                    .delay(Double(index) * 0.2),
                                value: animating
                            )
                    }
                    
                    Text("Thinking...")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.leading, 8)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.secondary.opacity(0.2))
                )
            }
            
            Spacer()
        }
        .onAppear {
            animating = true
        }
    }
}

// Quick Suggestion Card
struct QuickSuggestionCard: View {
    let icon: String
    let title: String
    let subtitle: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Image(systemName: icon)
                        .font(.system(size: 20))
                        .foregroundColor(.blue)
                    
                    Spacer()
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.headline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.secondary.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.secondary.opacity(0.4).opacity(0.3), lineWidth: 0.5)
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

// Chat History Item
struct ChatHistoryItem: View {
    let title: String
    let isActive: Bool
    
    var body: some View {
        HStack {
            Image(systemName: "bubble.left")
                .font(.system(size: 14))
                .foregroundColor(isActive ? .blue : .secondary)
            
            Text(title)
                .font(.system(size: 14))
                .foregroundColor(isActive ? .primary : .secondary)
                .lineLimit(1)
            
            Spacer()
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(isActive ? Color.blue.opacity(0.1) : Color.clear)
        )
    }
}

// Main Chat View
struct WisbeeChatView: View {
    @State private var messages: [ChatMessage] = []
    @State private var inputText: String = ""
    @State private var isLoading: Bool = false
    @State private var selectedModel: String = "llama3-8b-8192"
    @State private var showModelSelector: Bool = false
    @State private var showSidebar: Bool = false
    @State private var chatTitle: String = "New Chat"
    
    private let agent: WisbeeAgent
    
    init(agent: WisbeeAgent) {
        self.agent = agent
    }
    
    var body: some View {
        NavigationSplitView(sidebar: {
            sidebarView
        }, detail: {
            chatDetailView
        })
        .navigationSplitViewStyle(.balanced)
    }
    
    private var sidebarView: some View {
        VStack(spacing: 0) {
            // Sidebar Header
            HStack {
                Button(action: { startNewChat() }) {
                    HStack {
                        Image(systemName: "plus")
                        Text("New Chat")
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .padding(.horizontal, 16)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                
                Button(action: { showModelSelector.toggle() }) {
                    Image(systemName: "cpu")
                        .padding(12)
                        .background(Color.secondary.opacity(0.3))
                        .cornerRadius(8)
                }
            }
            .padding()
            
            // Chat History (placeholder)
            List {
                ChatHistoryItem(title: "Wisbeeについて", isActive: true)
                ChatHistoryItem(title: "プログラミングの質問", isActive: false)
                ChatHistoryItem(title: "料理のレシピ", isActive: false)
            }
            .listStyle(PlainListStyle())
            
            Spacer()
            
            // Model info
            VStack(alignment: .leading, spacing: 8) {
                Text("Current Model")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                HStack {
                    Circle()
                        .fill(Color.green)
                        .frame(width: 8, height: 8)
                    
                    Text(modelDisplayName(selectedModel))
                        .font(.caption)
                        .foregroundColor(.primary)
                }
                
                Text("Powered by Groq")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.secondary.opacity(0.2))
            .cornerRadius(8)
            .padding()
        }
        .frame(minWidth: 250, maxWidth: 300)
    }
    
    private var chatDetailView: some View {
        VStack(spacing: 0) {
            // Modern Header
            modernHeaderView
            
            // Messages Area
            messagesView
            
            // Input Area
            modernInputView
        }
        .background(Color(NSColor.controlBackgroundColor))
        .sheet(isPresented: $showModelSelector) {
            ModelSelectorView(selectedModel: $selectedModel)
        }
    }
    
    private var messagesView: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 24) {
                    // Welcome message if no messages
                    if messages.isEmpty {
                        welcomeView
                            .padding(.top, 40)
                    }
                    
                    ForEach(messages) { message in
                        ModernMessageBubble(message: message)
                            .id(message.id)
                    }
                    
                    if isLoading {
                        ModernLoadingIndicator()
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 100) // Space for input
            }
            .onChange(of: messages.count) {
                withAnimation(.easeInOut(duration: 0.5)) {
                    proxy.scrollTo(messages.last?.id, anchor: .bottom)
                }
            }
        }
    }
    
    private var welcomeView: some View {
        VStack(spacing: 24) {
            // Wisbee Logo/Icon
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.yellow.opacity(0.3), Color.orange.opacity(0.3)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 80, height: 80)
                
                Text("🐝")
                    .font(.system(size: 40))
            }
            
            VStack(spacing: 12) {
                Text("Welcome to Wisbee RAG")
                    .font(.title)
                    .fontWeight(.semibold)
                
                Text("I'm your AI assistant powered by advanced RAG technology.\nAsk me anything and I'll help you with contextual answers!")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(nil)
            }
            
            // Quick suggestions
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                QuickSuggestionCard(
                    icon: "lightbulb.fill",
                    title: "Wisbeeの特徴",
                    subtitle: "技術について教えて"
                ) {
                    inputText = "Wisbeeの特徴について教えてください"
                    sendMessage()
                }
                
                QuickSuggestionCard(
                    icon: "book.fill",
                    title: "使い方",
                    subtitle: "基本的な使い方"
                ) {
                    inputText = "Wisbeeの使い方を教えてください"
                    sendMessage()
                }
                
                QuickSuggestionCard(
                    icon: "cpu",
                    title: "RAG技術",
                    subtitle: "仕組みを知りたい"
                ) {
                    inputText = "RAG技術の仕組みについて説明してください"
                    sendMessage()
                }
                
                QuickSuggestionCard(
                    icon: "sparkles",
                    title: "何ができる？",
                    subtitle: "機能を知りたい"
                ) {
                    inputText = "Wisbeeで何ができますか？"
                    sendMessage()
                }
            }
        }
        .padding(32)
    }
    
    private var modernHeaderView: some View {
        HStack {
            Text(chatTitle)
                .font(.headline)
                .fontWeight(.medium)
            
            Spacer()
            
            HStack(spacing: 12) {
                Button(action: { showModelSelector.toggle() }) {
                    HStack(spacing: 6) {
                        Circle()
                            .fill(Color.green)
                            .frame(width: 6, height: 6)
                        
                        Text(modelDisplayName(selectedModel))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.secondary.opacity(0.2))
                    .cornerRadius(12)
                }
                
                Button(action: { startNewChat() }) {
                    Image(systemName: "plus")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.primary)
                        .frame(width: 32, height: 32)
                        .background(Color.secondary.opacity(0.2))
                        .cornerRadius(8)
                }
            }
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 16)
        .background(
            Color(NSColor.controlBackgroundColor)
                .shadow(color: Color.black.opacity(0.05), radius: 1, x: 0, y: 1)
        )
    }
    
    private var modernInputView: some View {
        VStack(spacing: 0) {
            // Input field
            HStack(spacing: 12) {
                HStack(spacing: 12) {
                    TextField("Type your message...", text: $inputText, axis: .vertical)
                        .lineLimit(1...6)
                        .font(.body)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .background(Color.secondary.opacity(0.2))
                        .cornerRadius(20)
                        .onSubmit {
                            sendMessage()
                        }
                    
                    Button(action: sendMessage) {
                        ZStack {
                            Circle()
                                .fill(inputText.isEmpty ? Color.secondary.opacity(0.4) : Color.blue)
                                .frame(width: 36, height: 36)
                            
                            Image(systemName: "arrow.up")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.white)
                        }
                    }
                    .disabled(inputText.isEmpty || isLoading)
                    .animation(.easeInOut(duration: 0.2), value: inputText.isEmpty)
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 16)
            .padding(.bottom, 24)
            .background(
                Color(NSColor.controlBackgroundColor)
                    .shadow(color: Color.black.opacity(0.05), radius: 1, x: 0, y: -1)
            )
        }
    }
    
    private func startNewChat() {
        messages.removeAll()
        inputText = ""
        chatTitle = "New Chat"
    }
    
    private func sendMessage() {
        guard !inputText.isEmpty else { return }
        
        let userMessage = ChatMessage(content: inputText, isUser: true)
        messages.append(userMessage)
        
        let query = inputText
        inputText = ""
        isLoading = true
        
        Task {
            do {
                let response = try await agent.runWithModel(question: query, model: selectedModel)
                await MainActor.run {
                    messages.append(ChatMessage(content: response, isUser: false))
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    messages.append(ChatMessage(
                        content: "エラーが発生しました: \(error.localizedDescription)",
                        isUser: false
                    ))
                    isLoading = false
                }
            }
        }
    }
    
    // Helper function for model display names
    private func modelDisplayName(_ model: String) -> String {
        switch model {
        case "llama3-8b-8192":
            return "Llama 3 8B"
        case "llama3-70b-8192":
            return "Llama 3 70B"
        case "llama-3.1-8b-instant":
            return "Llama 3.1 8B (Fast)"
        case "llama-3.3-70b-versatile":
            return "Llama 3.3 70B"
        case "deepseek-r1-distill-llama-70b":
            return "DeepSeek R1 70B"
        case "mistral-saba-24b":
            return "Mistral Saba 24B"
        case "gemma2-9b-it":
            return "Gemma 2 9B"
        case "qwen/qwen3-32b":
            return "Qwen 3 32B"
        case "qwen-qwq-32b":
            return "Qwen QwQ 32B"
        case "allam-2-7b":
            return "Allam 2 7B"
        case "compound-beta":
            return "Compound Beta"
        case "compound-beta-mini":
            return "Compound Beta Mini"
        default:
            return model
        }
    }
}

// Model Selector View
struct ModelSelectorView: View {
    @Binding var selectedModel: String
    @Environment(\.dismiss) private var dismiss
    
    private let availableModels = [
        ModelGroup(
            title: "Recommended",
            models: [
                GroqModel(id: "llama3-8b-8192", name: "Llama 3 8B", description: "Fast and reliable"),
                GroqModel(id: "deepseek-r1-distill-llama-70b", name: "DeepSeek R1 70B", description: "Advanced reasoning"),
                GroqModel(id: "llama-3.1-8b-instant", name: "Llama 3.1 8B (Fast)", description: "Ultra-fast responses")
            ]
        ),
        ModelGroup(
            title: "Large Models",
            models: [
                GroqModel(id: "llama3-70b-8192", name: "Llama 3 70B", description: "High quality responses"),
                GroqModel(id: "llama-3.3-70b-versatile", name: "Llama 3.3 70B", description: "Latest Llama model")
            ]
        ),
        ModelGroup(
            title: "Specialized",
            models: [
                GroqModel(id: "mistral-saba-24b", name: "Mistral Saba 24B", description: "Mistral's latest"),
                GroqModel(id: "gemma2-9b-it", name: "Gemma 2 9B", description: "Google's model"),
                GroqModel(id: "qwen/qwen3-32b", name: "Qwen 3 32B", description: "Alibaba's model"),
                GroqModel(id: "qwen-qwq-32b", name: "Qwen QwQ 32B", description: "Reasoning focused"),
                GroqModel(id: "allam-2-7b", name: "Allam 2 7B", description: "IBM's model"),
                GroqModel(id: "compound-beta", name: "Compound Beta", description: "Experimental"),
                GroqModel(id: "compound-beta-mini", name: "Compound Beta Mini", description: "Lightweight")
            ]
        )
    ]
    
    var body: some View {
        NavigationView {
            List {
                ForEach(availableModels, id: \.title) { group in
                    Section(group.title) {
                        ForEach(group.models, id: \.id) { model in
                            ModelRowView(
                                model: model,
                                isSelected: selectedModel == model.id
                            ) {
                                selectedModel = model.id
                                dismiss()
                            }
                        }
                    }
                }
            }
            .navigationTitle("Select Model")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                #if os(iOS)
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
                #else
                ToolbarItem(placement: .automatic) {
                    Button("Done") {
                        dismiss()
                    }
                }
                #endif
            }
        }
    }
}

struct ModelGroup {
    let title: String
    let models: [GroqModel]
}

struct GroqModel {
    let id: String
    let name: String
    let description: String
}

struct ModelRowView: View {
    let model: GroqModel
    let isSelected: Bool
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(model.name)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(model.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.blue)
                }
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Main App

// Mock retriever for testing
class MockRetriever: ObjectBoxRetriever {
    init() {
        super.init(documents: [
            VectorDocument(content: "Wisbeeは、世界初のText-to-LoRA技術を搭載したAIアシスタントです。", embedding: []),
            VectorDocument(content: "jan-nano XSモデル（Q4_K_XS量子化）を使用して、高速かつ効率的な推論を実現しています。", embedding: []),
            VectorDocument(content: "70以上のカテゴリーで学習されたWisbeeキャラクターは、幅広い知識を持っています。", embedding: [])
        ])
    }
}

struct LoadingView: View {
    var body: some View {
        VStack(spacing: 20) {
            ProgressView()
                .scaleEffect(1.5)
            
            Text("🐝 Wisbee RAGを初期化中...")
                .font(.title3)
                .foregroundColor(.secondary)
        }
    }
}

struct ErrorView: View {
    let message: String
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 60))
                .foregroundColor(.red)
            
            Text("エラーが発生しました")
                .font(.title2)
                .fontWeight(.bold)
            
            Text(message)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
    }
}

@main
struct WisbeeApp: App {
    @State private var agent: WisbeeAgent?
    @State private var isLoading = true
    @State private var errorMessage: String?
    
    var body: some Scene {
        WindowGroup {
            if isLoading {
                LoadingView()
                    .task {
                        await initializeAgent()
                    }
            } else if let agent = agent {
                WisbeeChatView(agent: agent)
            } else {
                ErrorView(message: errorMessage ?? "Failed to initialize")
            }
        }
    }
    
    private func initializeAgent() async {
        do {
            // Initialize ObjectBox Store
            let appSupport = FileManager.default.urls(for: .applicationSupportDirectory,
                                                     in: .userDomainMask).first!
            let storeDirectory = appSupport.appendingPathComponent("WisbeeRAG/db")
            try FileManager.default.createDirectory(at: storeDirectory,
                                                  withIntermediateDirectories: true)
            
            // For ObjectBox 1.9, we need to create store differently
            // Since we can't use code generation easily, let's use a simpler approach
            print("Store directory: \(storeDirectory.path)")
            
            // Create mock agent with in-memory data
            let mockRetriever = MockRetriever()
            let agent = WisbeeAgent(modelPath: "model.gguf", retriever: mockRetriever)
            
            // Set up API client with Groq
            let apiKey = "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"
            let apiClient = WisbeeAPIClient(apiKey: apiKey)
            agent.setAPIClient(apiClient)
            
            await MainActor.run {
                self.agent = agent
                self.isLoading = false
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
}